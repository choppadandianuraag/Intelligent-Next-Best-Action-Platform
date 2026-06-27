import json
import time
from typing import Optional

from backend.memory.episodic import EpisodicMemory
from backend.models.schemas import AgentStep


# ---------------------------------------------------------------------------
# Model abstraction — swap this out when your open-source model is ready
# ---------------------------------------------------------------------------
def _call_model(risk: dict, knowledge: list, memory_context: dict) -> Optional[str]:
    """
    Stub: rule-based NBA generation so the pipeline runs end-to-end
    without a real model. Replace with your open-source model later.
    """
    risk_level = risk.get("risk_level", "medium")
    risk_score = risk.get("risk_score", 0.5)
    signal_count = risk.get("signal_count", 0)
    risk_factors = risk.get("risk_factors", [])

    has_memory = memory_context.get("similar_cases_found", 0) > 0
    precedent_accounts = memory_context.get("precedent_accounts", [])

    # Determine primary recommendation based on risk level
    if risk_level == "critical":
        primary = {
            "title": "Schedule Executive Business Review (EBR)",
            "description": (
                f"Account is at critical risk (score: {risk_score}). "
                "Schedule an Executive Business Review within 48 hours to address "
                "the identified risk factors and prevent churn."
            ),
            "confidence": 0.73,
            "estimated_impact": "High — addresses critical churn risk head-on",
            "evidence_ids": list(dict.fromkeys(rf for rf in risk_factors[:3] if rf)) or ["ev_0"],
            "precedent_accounts": precedent_accounts,
        }
        alternatives = [
            {
                "title": "Send executive escalation to VP of Customer Success",
                "description": (
                    "Escalate the situation to leadership with a full risk report "
                    "and proposed intervention plan."
                ),
                "confidence": 0.60,
                "estimated_impact": "Medium — ensures leadership visibility",
                "evidence_ids": list(dict.fromkeys(rf for rf in risk_factors[:2] if rf)) or ["ev_0"],
                "precedent_accounts": precedent_accounts,
            },
            {
                "title": "Conduct technical deep-dive session",
                "description": (
                    "Schedule a technical session to address product adoption gaps "
                    "and demonstrate value of unused features."
                ),
                "confidence": 0.55,
                "estimated_impact": "Medium — may improve product adoption",
                "evidence_ids": list(dict.fromkeys(rf for rf in risk_factors[:1] if rf)) or ["ev_0"],
                "precedent_accounts": precedent_accounts,
            },
        ]
    elif risk_level == "high":
        primary = {
            "title": "Schedule targeted intervention call",
            "description": (
                f"Account shows high risk (score: {risk_score}). Schedule a focused "
                "intervention call with the CSM to address specific concerns and "
                "present a remediation plan."
            ),
            "confidence": 0.73,
            "estimated_impact": "High — addresses risk before it escalates",
            "evidence_ids": list(dict.fromkeys(rf for rf in risk_factors[:3] if rf)) or ["ev_0"],
            "precedent_accounts": precedent_accounts,
        }
        alternatives = [
            {
                "title": "Prepare custom success plan with milestones",
                "description": "Create a tailored success plan with measurable milestones to rebuild confidence.",
                "confidence": 0.62,
                "estimated_impact": "Medium — provides structured path forward",
                "evidence_ids": list(dict.fromkeys(rf for rf in risk_factors[:2] if rf)) or ["ev_0"],
                "precedent_accounts": precedent_accounts,
            },
            {
                "title": "Offer discounted renewal with value-add services",
                "description": "Propose a renewal package with additional services at a discount to retain the account.",
                "confidence": 0.50,
                "estimated_impact": "Medium — financial incentive to stay",
                "evidence_ids": list(dict.fromkeys(rf for rf in risk_factors[:1] if rf)) or ["ev_0"],
                "precedent_accounts": precedent_accounts,
            },
        ]
    elif risk_level == "medium":
        primary = {
            "title": "Schedule Quarterly Business Review (QBR)",
            "description": (
                f"Account shows moderate risk (score: {risk_score}). Schedule a QBR "
                "to review performance, address concerns, and identify expansion opportunities."
            ),
            "confidence": 0.73,
            "estimated_impact": "Medium — maintains relationship and identifies opportunities",
            "evidence_ids": list(dict.fromkeys(rf for rf in risk_factors[:2] if rf)) or ["ev_0"],
            "precedent_accounts": precedent_accounts,
        }
        alternatives = [
            {
                "title": "Conduct health check survey",
                "description": "Send a customer health check survey to gather more data on satisfaction levels.",
                "confidence": 0.55,
                "estimated_impact": "Low — provides additional signal data",
                "evidence_ids": list(dict.fromkeys(rf for rf in risk_factors[:1] if rf)) or ["ev_0"],
                "precedent_accounts": precedent_accounts,
            },
            {
                "title": "Share relevant playbook articles",
                "description": "Share playbook articles addressing the identified risk factors with the customer.",
                "confidence": 0.45,
                "estimated_impact": "Low — educational value, limited direct impact",
                "evidence_ids": list(dict.fromkeys(rf for rf in risk_factors[:1] if rf)) or ["ev_0"],
                "precedent_accounts": precedent_accounts,
            },
        ]
    else:  # low risk
        primary = {
            "title": "Propose enterprise upgrade or expansion",
            "description": (
                f"Account is healthy (score: {risk_score}, {signal_count} positive signals). "
                "Propose an enterprise upgrade, expansion to new teams, or API access "
                "to capitalize on engagement."
            ),
            "confidence": 0.73,
            "estimated_impact": "High — captures expansion opportunity",
            "evidence_ids": list(dict.fromkeys(rf for rf in risk_factors[:2] if rf)) or ["ev_0"],
            "precedent_accounts": precedent_accounts,
        }
        alternatives = [
            {
                "title": "Request customer referral or case study",
                "description": "Ask the satisfied customer for a referral or case study to drive new business.",
                "confidence": 0.60,
                "estimated_impact": "Medium — generates pipeline and social proof",
                "evidence_ids": list(dict.fromkeys(rf for rf in risk_factors[:1] if rf)) or ["ev_0"],
                "precedent_accounts": precedent_accounts,
            },
            {
                "title": "Schedule product roadmap review",
                "description": "Share upcoming product roadmap and gather feedback on future priorities.",
                "confidence": 0.55,
                "estimated_impact": "Medium — strengthens partnership and alignment",
                "evidence_ids": list(dict.fromkeys(rf for rf in risk_factors[:1] if rf)) or ["ev_0"],
                "precedent_accounts": precedent_accounts,
            },
        ]

    result = {
        "primary": primary,
        "alternatives": alternatives,
    }
    return json.dumps(result)


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
    risk_level = risk.get("risk_level", "medium")
    risk_score = risk.get("risk_score", 0.5)

    # Get memory context from episodic memory
    memory = EpisodicMemory()
    memory_context = memory.get_memory_context(
        risk_level=risk_level, risk_score=risk_score
    )

    prompt = (
        "You are a customer success strategist. Given the risk assessment, "
        "knowledge, and past resolved cases, recommend 3 actions.\n"
        "Return ONLY JSON with keys: primary (Action), alternatives (list of 2 Actions).\n"
        "Action schema: {title, description, confidence (0.0-1.0), estimated_impact, "
        "evidence_ids, precedent_accounts}\n\n"
        f"Risk: {json.dumps(risk, indent=2)}\n"
        f"Knowledge: {json.dumps(knowledge, indent=2)}\n"
        f"Memory: {json.dumps(memory_context.model_dump(), indent=2)}"
    )

    try:
        raw_response = _call_model(risk, knowledge, memory_context.model_dump())
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
    }
