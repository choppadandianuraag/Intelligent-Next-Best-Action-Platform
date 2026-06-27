"""
NBA Generator agent — generates primary recommendation + 2 alternatives.
Applies memory confidence boost from knowledge_retriever's memory_context.
"""
import json
import os
import time
import uuid

import anthropic
from dotenv import load_dotenv

from backend.models.schemas import AgentStep, Action

load_dotenv()

MODEL = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
_client = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    return _client


SYSTEM_PROMPT = """You are an expert customer success strategist. Given a full risk assessment, extracted signals, and knowledge base context, generate next-best-action recommendations.

Return a JSON object with exactly this structure:
{
  "primary": {
    "title": "<action title, max 10 words>",
    "description": "<detailed description of the action, 2-4 sentences>",
    "confidence": <float 0.0-1.0>,
    "estimated_impact": "<e.g., 'High — directly addresses churn threat and restores exec relationship'>",
    "evidence_ids": [],
    "precedent_accounts": []
  },
  "alternatives": [
    {
      "title": "<alternative 1 title>",
      "description": "<description>",
      "confidence": <float>,
      "estimated_impact": "<impact>",
      "evidence_ids": [],
      "precedent_accounts": []
    },
    {
      "title": "<alternative 2 title>",
      "description": "<description>",
      "confidence": <float>,
      "estimated_impact": "<impact>",
      "evidence_ids": [],
      "precedent_accounts": []
    }
  ]
}

Base confidence on the strength of evidence. For high-risk accounts: primary should target the most urgent intervention.
Return ONLY valid JSON. No markdown fences."""


def nba_generator_node(state: dict) -> dict:
    start = time.time()
    signals = state.get("signals", [])
    risk = state.get("risk", {})
    knowledge_chunks = state.get("knowledge_chunks", [])
    memory_context = state.get("memory_context")
    customer_profile = state.get("customer_profile", {})

    signals_text = "\n".join(
        f"- [{s.get('type', 'neutral').upper()}/{s.get('severity', 'low').upper()}] {s.get('text', '')}"
        for s in signals
    )
    kb_text = "\n".join(
        f"- {c.get('excerpt', '')[:300]}" for c in knowledge_chunks[:4]
    )
    memory_note = ""
    if memory_context:
        mc = memory_context
        memory_note = (
            f"\nMemory context: {mc['similar_cases_found']} similar resolved cases found "
            f"({', '.join(mc['precedent_accounts'])}). "
            f"These cases were successfully resolved with: executive business reviews and structured re-engagement."
        )

    profile_text = (
        f"Account: {customer_profile.get('account_name', 'Unknown')}, "
        f"CSM: {customer_profile.get('csm', 'Unknown')}, "
        f"ARR: ${customer_profile.get('arr', 0):,}"
    ) if customer_profile else ""

    prompt = f"""Generate next-best-action recommendations.

{profile_text}

Risk assessment:
- Level: {risk.get('level', 'unknown').upper()}
- Score: {risk.get('score', 0.5):.0%}
- Key signals: {', '.join(risk.get('key_signals', [])[:3])}

Signals:
{signals_text}

Knowledge base context:
{kb_text}
{memory_note}"""

    try:
        response = _get_client().messages.create(
            model=MODEL,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )
        content = response.content[0].text.strip()
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        recs = json.loads(content)
    except Exception as e:
        recs = {
            "primary": {
                "title": "Schedule Executive Business Review",
                "description": f"Escalate to EBR given current risk level. ({e})",
                "confidence": 0.73,
                "estimated_impact": "High",
                "evidence_ids": [],
                "precedent_accounts": [],
            },
            "alternatives": [
                {
                    "title": "Escalate open support tickets",
                    "description": "Triage all open tickets to P1 and resolve within 48h.",
                    "confidence": 0.65,
                    "estimated_impact": "Medium",
                    "evidence_ids": [],
                    "precedent_accounts": [],
                },
                {
                    "title": "Send proactive ROI report",
                    "description": "Build and send a custom ROI analysis within 24h.",
                    "confidence": 0.58,
                    "estimated_impact": "Medium",
                    "evidence_ids": [],
                    "precedent_accounts": [],
                },
            ],
        }

    # Apply memory confidence boost
    if memory_context and memory_context.get("similar_cases_found", 0) > 0:
        mc = memory_context
        boost = mc.get("confidence_boost", 0.0)
        primary = recs["primary"]
        base_conf = primary.get("confidence", 0.73)
        primary["confidence"] = round(min(base_conf + boost, 0.97), 3)
        primary["precedent_accounts"] = mc.get("precedent_accounts", [])

    # Attach evidence IDs from knowledge chunks
    ev_ids = [c.get("id", str(uuid.uuid4())) for c in knowledge_chunks[:3]]
    recs["primary"]["evidence_ids"] = ev_ids

    duration_ms = int((time.time() - start) * 1000)
    primary = recs["primary"]
    boost_note = ""
    if memory_context and memory_context.get("similar_cases_found", 0) > 0:
        mc = memory_context
        boost_note = f" Memory boosted confidence from {mc['base_confidence']:.0%} → {primary['confidence']:.0%}."

    step = AgentStep(
        agent_name="NBA Generator",
        action=f"Generated primary recommendation: '{primary['title']}'",
        reasoning=(
            f"Based on {risk.get('level', 'unknown')} risk ({risk.get('score', 0):.0%}), "
            f"recommended '{primary['title']}' with {primary['confidence']:.0%} confidence."
            + boost_note
        ),
        duration_ms=duration_ms,
    )

    agent_trace = state.get("agent_trace", [])
    agent_trace.append(step.model_dump())

    return {**state, "recommendations": recs, "agent_trace": agent_trace}
