import json
import time
from typing import Optional

from backend.agents.llm_client import call_llm
from backend.memory.episodic import EpisodicMemory
from backend.models.schemas import AgentStep


# ---------------------------------------------------------------------------
# LLM-powered NBA generation
# ---------------------------------------------------------------------------
def _build_prompt(risk: dict, knowledge: list, memory_context: dict, account_data: dict | None = None) -> str:
    """Build the LLM prompt for recommendation generation."""
    # Format knowledge chunks (limit to keep prompt manageable)
    knowledge_lines = []
    for i, k in enumerate(knowledge, 1):
        excerpt = k.get("excerpt", "")
        source = k.get("source_name", "unknown")
        stype = k.get("source_type", "")
        if len(excerpt) > 200:
            excerpt = excerpt[:200] + "..."
        knowledge_lines.append(f"  {i}. [{stype}] {source}: {excerpt}")
    knowledge_str = "\n".join(knowledge_lines) if knowledge_lines else "  (no relevant knowledge found)"

    # Account context
    account_context = ""
    if account_data:
        account_context = (
            f"\n## Account Context\n"
            f"  Name: {account_data.get('account_name', 'N/A')}\n"
            f"  Industry: {account_data.get('industry', 'N/A')}\n"
            f"  Region: {account_data.get('region', 'N/A')}\n"
            f"  ARR: {account_data.get('arr_inr_display', 'N/A')}\n"
            f"  Contract End: {account_data.get('contract_end', 'N/A')}\n"
            f"  CSM: {account_data.get('csm', 'N/A')}\n"
            f"  Current NPS: {account_data.get('nps_score', 'N/A')}\n"
        )

    precedent_str = ""
    if memory_context.get("precedent_accounts"):
        precedent_str = (
            "\nPrecedent accounts with similar resolved situations:\n"
            + "\n".join(f"  - {a}" for a in memory_context["precedent_accounts"])
            + "\n"
        )

    return (
        "You are a senior customer success strategist. Based on the risk assessment, "
        "supporting knowledge, and past resolved cases below, generate 3 concrete "
        "next-best actions for the CSM.\n\n"
        f"## Risk Assessment\n"
        f"  Score: {risk.get('risk_score', 'N/A')} ({risk.get('risk_level', 'N/A')})\n"
        f"  Signals detected: {risk.get('signal_count', 0)}\n"
        f"  Risk factors: {json.dumps(risk.get('risk_factors', []))}\n"
        f"{account_context}"
        f"\n## Supporting Knowledge Evidence\n{knowledge_str}\n"
        f"\n## Memory Context\n"
        f"  Similar resolved cases found: {memory_context.get('similar_cases_found', 0)}\n"
        f"  Memory confidence boost: +{memory_context.get('confidence_boost', 0)}\n"
        f"{precedent_str}"
        "\n## Instructions\n"
        "Return ONLY a JSON object with these exact keys:\n"
        '{\n'
        '  "primary": {\n'
        '    "title": <string, concise actionable title>,\n'
        '    "description": <string, 2-3 sentences explaining the action and why>,\n'
        '    "confidence": <float 0.0-1.0, your confidence this is the right action>,\n'
        '    "estimated_impact": <string, e.g. "High — prevents churn">,\n'
        '    "evidence_ids": <list of strings, reference evidence IDs>,\n'
        '    "precedent_accounts": <list of strings>\n'
        "  },\n"
        '  "alternatives": [\n'
        '    {same schema as primary},\n'
        '    {same schema as primary}\n'
        "  ]\n"
        "}\n\n"
        "Guidelines:\n"
        "- Make recommendations SPECIFIC to the account context, not generic templates\n"
        '- "confidence" should reflect how certain you are: 0.7-0.9 for clear patterns, '
        "0.4-0.6 for ambiguous situations\n"
        "- For critical/high risk: recommend immediate, concrete intervention steps\n"
        "- For low risk: recommend expansion, upsell, or relationship-deepening actions\n"
        "- Reference specific evidence (playbooks, meeting notes, or resolved cases) "
        "in evidence_ids\n"
        "- If precedent accounts exist, reference what worked for them in the descriptions\n"
        "- The description should be useful enough that a CSM could act on it immediately\n"
    )


def _call_model(risk: dict, knowledge: list, memory_context: dict, account_data: dict | None = None) -> Optional[str]:
    """
    Call the LLM to generate context-specific next-best-action recommendations.
    Returns a JSON string with 'primary' and 'alternatives' keys.
    Falls back to rule-based templates if the LLM call fails.
    """
    prompt = _build_prompt(risk, knowledge, memory_context, account_data)

    try:
        raw_response = call_llm(
            prompt,
            max_tokens=2048,
            temperature=0.2,  # slight creativity for diverse alternatives
            json_mode=True,
        )
        return raw_response
    except Exception:
        # Fallback: rule-based templates so the pipeline never breaks
        risk_level = risk.get("risk_level", "medium")
        risk_score = risk.get("risk_score", 0.5)
        signal_count = risk.get("signal_count", 0)
        risk_factors = risk.get("risk_factors", [])
        precedent_accounts = memory_context.get("precedent_accounts", [])

        def _fallback_action(title, desc, conf, impact):
            return {
                "title": title,
                "description": desc,
                "confidence": conf,
                "estimated_impact": impact,
                "evidence_ids": ["ev_0"],
                "precedent_accounts": precedent_accounts,
            }

        if risk_level == "critical":
            primary = _fallback_action(
                "Schedule Executive Business Review (EBR)",
                f"Account is at critical risk (score: {risk_score}). "
                "Schedule an Executive Business Review within 48 hours.",
                0.73, "High — addresses critical churn risk head-on"
            )
            alternatives = [
                _fallback_action(
                    "Send executive escalation to VP of Customer Success",
                    "Escalate to leadership with a full risk report.", 0.60,
                    "Medium — ensures leadership visibility"
                ),
                _fallback_action(
                    "Conduct technical deep-dive session",
                    "Address product adoption gaps and demonstrate value.", 0.55,
                    "Medium — may improve product adoption"
                ),
            ]
        elif risk_level == "high":
            primary = _fallback_action(
                "Schedule targeted intervention call",
                f"Account shows high risk (score: {risk_score}). "
                "Schedule a focused intervention call to address specific concerns.",
                0.73, "High — addresses risk before it escalates"
            )
            alternatives = [
                _fallback_action(
                    "Prepare custom success plan with milestones",
                    "Create a tailored success plan with measurable milestones.", 0.62,
                    "Medium — provides structured path forward"
                ),
                _fallback_action(
                    "Offer discounted renewal with value-add services",
                    "Propose a renewal package with additional services.", 0.50,
                    "Medium — financial incentive to stay"
                ),
            ]
        elif risk_level == "medium":
            primary = _fallback_action(
                "Schedule Quarterly Business Review (QBR)",
                f"Account shows moderate risk (score: {risk_score}). "
                "Schedule a QBR to review performance and identify opportunities.",
                0.73, "Medium — maintains relationship and identifies opportunities"
            )
            alternatives = [
                _fallback_action(
                    "Conduct health check survey",
                    "Send a structured survey to gather satisfaction data.", 0.55,
                    "Low — provides additional signal data"
                ),
                _fallback_action(
                    "Share relevant playbook articles",
                    "Share playbook articles addressing identified risk factors.", 0.45,
                    "Low — educational value"
                ),
            ]
        else:  # low risk
            primary = _fallback_action(
                "Propose enterprise upgrade or expansion",
                f"Account is healthy (score: {risk_score}). "
                "Propose expansion, upgrade, or API access to capitalize on engagement.",
                0.73, "High — captures expansion opportunity"
            )
            alternatives = [
                _fallback_action(
                    "Request customer referral or case study",
                    "Ask the satisfied customer for a referral to drive new business.", 0.60,
                    "Medium — generates pipeline and social proof"
                ),
                _fallback_action(
                    "Schedule product roadmap review",
                    "Share upcoming roadmap and gather feedback on priorities.", 0.55,
                    "Medium — strengthens partnership"
                ),
            ]

        return json.dumps({"primary": primary, "alternatives": alternatives})


def _parse_recommendations(raw: str) -> dict:
    """Strip markdown fences and parse JSON recommendations."""
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[-1]
        cleaned = cleaned.rsplit("```", 1)[0]
        cleaned = cleaned.strip()

    parsed = json.loads(cleaned)
    if "primary" not in parsed:
        raise ValueError("Missing 'primary' key in recommendations")
    if "alternatives" not in parsed:
        raise ValueError("Missing 'alternatives' key in recommendations")
    if not isinstance(parsed["alternatives"], list) or len(parsed["alternatives"]) < 2:
        raise ValueError("Need at least 2 alternatives")
    return parsed


def generate(state: dict) -> dict:
    """
    NBA Generator node: produces 3 next-best-action recommendations
    (1 primary + 2 alternatives) with confidence scoring and memory boost.
    """
    start = time.time()

    risk = state.get("risk", {})
    knowledge = state.get("knowledge_chunks", [])
    account_data = state.get("account_data", {})
    risk_level = risk.get("risk_level", "medium")
    risk_score = risk.get("risk_score", 0.5)

    # Get memory context from episodic memory
    memory = EpisodicMemory()
    memory_context = memory.get_memory_context(
        risk_level=risk_level, risk_score=risk_score
    )

    try:
        raw_response = _call_model(risk, knowledge, memory_context.model_dump(), account_data)
        parsed = _parse_recommendations(raw_response)

        primary = parsed["primary"]
        alternatives = parsed["alternatives"]

        # Apply memory confidence boost formula
        base_confidence = primary.get("confidence", 0.73)
        similar_count = memory_context.similar_cases_found
        boosted = min(base_confidence * (1 + 0.06 * similar_count), 0.97)
        primary["confidence"] = round(boosted, 3)
        primary["precedent_accounts"] = memory_context.precedent_accounts
        for alt in alternatives:
            alt["precedent_accounts"] = memory_context.precedent_accounts

        reasoning = f"Primary: {primary['title']}, confidence: {primary['confidence']}"

    except Exception as e:
        primary = {
            "title": "Schedule follow-up call",
            "description": "A follow-up call is recommended to better understand customer needs and address any concerns.",
            "confidence": 0.5,
            "estimated_impact": "Medium",
            "evidence_ids": [],
            "precedent_accounts": [],
        }
        alternatives = [
            {
                "title": "Send customer satisfaction survey",
                "description": "Gather feedback through a structured survey to identify areas for improvement.",
                "confidence": 0.4,
                "estimated_impact": "Low",
                "evidence_ids": [],
                "precedent_accounts": [],
            },
            {
                "title": "Share product documentation",
                "description": "Share relevant documentation and resources to help the customer get more value.",
                "confidence": 0.3,
                "estimated_impact": "Low",
                "evidence_ids": [],
                "precedent_accounts": [],
            },
        ]
        reasoning = f"Recommendation generation failed: {str(e)}"

    duration_ms = max(1, round((time.time() - start) * 1000))

    step = {
        "agent_name": "nba_generator",
        "action": "generated_recommendations",
        "reasoning": reasoning,
        "duration_ms": duration_ms,
    }
    state["agent_trace"].append(step)

    return {
        "recommendations": {"primary": primary, "alternatives": alternatives},
        "agent_trace": state["agent_trace"],
        "memory_context": memory_context.model_dump(),
    }
