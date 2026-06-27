"""
Risk Assessor agent — prompts Groq to score churn risk 0-100% and classify level.
Returns risk: dict with score (float 0-1), level, signal_count, key_signals.
"""
import json
import os
import time

from groq import Groq
from dotenv import load_dotenv

from backend.models.schemas import AgentStep

load_dotenv()

MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
_client = None


def _get_client() -> Groq:
    global _client
    if _client is None:
        _client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    return _client


SYSTEM_PROMPT = """You are a customer success risk analyst. Given extracted signals from a customer interaction and relevant knowledge base context, assess churn risk.

Return a JSON object with exactly these fields:
{
  "score": <float 0.0-1.0, the churn probability>,
  "level": <"critical" | "high" | "medium" | "low">,
  "signal_count": <integer count of risk signals>,
  "key_signals": [<list of up to 4 most important risk signal texts>],
  "reasoning": <2-3 sentence explanation of the score>
}

Scoring guide:
- critical: 0.80-1.0 (explicit churn threat, renewal <30 days, competitor evaluation + multiple signals)
- high: 0.60-0.79 (1-2 serious risk signals, declining health indicators)
- medium: 0.35-0.59 (some friction but engaged, onboarding struggles, single risk signal)
- low: 0.0-0.34 (healthy account, expansion signals, high engagement)

Return ONLY valid JSON. No markdown fences."""


def risk_assessor_node(state: dict) -> dict:
    start = time.time()
    signals = state.get("signals", [])
    knowledge_chunks = state.get("knowledge_chunks", [])
    customer_profile = state.get("customer_profile", {})

    # Build context for Groq
    risk_signals = [s for s in signals if s.get("type") == "risk"]
    signals_text = "\n".join(
        f"- [{s.get('severity', 'medium').upper()}] {s.get('text', '')}" for s in signals
    )
    kb_context = "\n".join(
        f"- {c.get('excerpt', '')[:200]}" for c in knowledge_chunks[:3]
    )
    profile_text = (
        f"Account: {customer_profile.get('account_name', 'Unknown')}, "
        f"ARR: ${customer_profile.get('arr', 0):,}, "
        f"Health score trend: {customer_profile.get('health_score_history', [])}, "
        f"Open tickets: {customer_profile.get('open_tickets', 0)}, "
        f"NPS: {customer_profile.get('nps_score', 'N/A')}, "
        f"Contract end: {customer_profile.get('contract_end', 'N/A')}"
    ) if customer_profile else "No CRM profile available"

    prompt = f"""Assess churn risk for this customer.

Customer Profile:
{profile_text}

Signals from interaction:
{signals_text}

Relevant knowledge context:
{kb_context}"""

    try:
        response = _get_client().chat.completions.create(
            model=MODEL,
            max_tokens=512,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
        )
        content = response.choices[0].message.content.strip()
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        risk = json.loads(content)
    except Exception as e:
        risk = {
            "score": 0.5,
            "level": "medium",
            "signal_count": len(risk_signals),
            "key_signals": [s.get("text", "") for s in risk_signals[:4]],
            "reasoning": f"Risk assessment failed ({e}); defaulting to medium.",
        }

    duration_ms = int((time.time() - start) * 1000)

    step = AgentStep(
        agent_name="Risk Assessor",
        action=f"Risk assessed: {risk['level'].upper()} ({risk['score']:.0%})",
        reasoning=risk.get("reasoning", f"Score: {risk['score']:.2f}, Level: {risk['level']}"),
        duration_ms=duration_ms,
    )

    agent_trace = state.get("agent_trace", [])
    agent_trace.append(step.model_dump())

    return {**state, "risk": risk, "agent_trace": agent_trace}
