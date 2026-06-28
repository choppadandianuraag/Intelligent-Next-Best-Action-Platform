import json
import time
from typing import Optional

from backend.agents.llm_client import call_llm
from backend.models.schemas import AgentStep


# ---------------------------------------------------------------------------
# LLM-powered risk assessment
# ---------------------------------------------------------------------------
def _build_prompt(signals: list, knowledge_chunks: list, account_data: dict | None = None) -> str:
    """Build the LLM prompt for risk assessment."""
    signal_lines = []
    for i, s in enumerate(signals, 1):
        signal_lines.append(
            f"  Signal {i}: \"{s.get('text', '')}\" | type={s.get('type', '')} | severity={s.get('severity', '')}"
        )
    signals_str = "\n".join(signal_lines) if signal_lines else "  (none)"

    knowledge_lines = []
    for i, k in enumerate(knowledge_chunks, 1):
        excerpt = k.get("excerpt", "")
        source = k.get("source_name", "unknown")
        # Truncate long excerpts to keep prompt size manageable
        if len(excerpt) > 300:
            excerpt = excerpt[:300] + "..."
        knowledge_lines.append(f"  Source {i}: [{source}] {excerpt}")
    knowledge_str = "\n".join(knowledge_lines) if knowledge_lines else "  (none)"

    # Account profile context (optional)
    account_context = ""
    if account_data:
        curr_risk = account_data.get("risk_level", "unknown")
        industry = account_data.get("industry", "unknown")
        arr = account_data.get("arr_inr_display", "")
        region = account_data.get("region", "")
        contract_end = account_data.get("contract_end", "unknown")
        nps = account_data.get("nps_score", "N/A")
        account_context = (
            f"## Account Profile\n"
            f"  Industry: {industry}\n"
            f"  Region: {region}\n"
            f"  ARR: {arr}\n"
            f"  Current CRM Risk Level: {curr_risk}\n"
            f"  Contract End: {contract_end}\n"
            f"  NPS Score: {nps}\n\n"
        )

    return (
        "You are a senior customer success risk analyst. Your task is to assess the "
        "churn risk for a B2B SaaS account based on signals extracted from a meeting "
        "transcript and supporting knowledge articles.\n\n"
        f"## Extracted Signals\n{signals_str}\n\n"
        f"{account_context}"
        f"## Supporting Knowledge\n{knowledge_str}\n\n"
        "## Instructions\n"
        "Analyze the signals holistically. Follow these principles:\n"
        "1. **Distinguish operational feedback from churn risk** — A customer asking for "
        "a mobile app improvement or raising a scale concern is often a GROWTH signal "
        "(they are engaged and planning to expand), NOT a churn risk.\n"
        "2. **Signal combinations multiply risk** — E.g., 'budget pressure' + "
        "'competitor evaluation' together is worse than either alone.\n"
        "3. **Positive signals show engagement, but do NOT cap the score** — Even if "
        "there are 2-3 positive signals, structural risks (budget cuts, renewal "
        "proximity, pricing demands) dominate. A customer saying 'the product is useful "
        "BUT we have a 30% cost reduction mandate' is still at risk. Score based on "
        "the worst risks, not the average of all signals.\n"
        "4. **Scale concerns are not churn risks** — Customers asking 'will it scale "
        "to 80 cities?' or requesting better features are demonstrating commitment. "
        "Treat these as low-risk unless accompanied by actual dissatisfaction.\n"
        "5. **Separate feedback from threats** — Someone saying 'the mobile app needs "
        "work' is product feedback. Someone saying 'we'll leave if you don't fix it' "
        "is a churn signal. Know the difference.\n"
        "6. **Renewal proximity escalates risk** — If the contract is ending within 60 "
        "days and there are unresolved risk signals, raise the score by at least "
        "one tier. A 22-day renewal with budget pressure is critical, not medium.\n"
        "7. **Budget / cost reduction mandates are structural risks** — Company-wide "
        "SaaS reduction mandates, CFO-driven cuts, or demands for 15-20% pricing "
        "reductions are not ordinary feedback. These are executive-level churn signals "
        "that put the entire renewal at risk regardless of user satisfaction.\n\n"
        "Return ONLY a JSON object with these exact keys:\n"
        '{\n'
        '  "risk_score": <float 0.0 to 1.0>,\n'
        '  "risk_level": <"critical"|"high"|"medium"|"low">,\n'
        '  "signal_count": <int>,\n'
        '  "risk_factors": [<string explanations of each factor>]\n'
        "}\n\n"
        "Guidelines for the score:\n"
        "- 0.80-1.00: critical (immediate escalation needed, multiple high-severity risks)\n"
        "- 0.50-0.79: high (active intervention required, significant concerns)\n"
        "- 0.25-0.49: medium (monitor and engage, mixed signals)\n"
        "- 0.00-0.24: low (account is healthy, positive or neutral signals dominate)\n\n"
        "Each risk_factor should be a concrete, actionable observation "
        "(e.g., 'Budget reduction mandate with urgency — pricing answer needed within 24h')."
    )


def _call_model(signals: list, knowledge_chunks: list, account_data: dict | None = None) -> Optional[str]:
    """
    Call the LLM to assess churn risk from signals and knowledge.
    Returns a JSON string with risk_score, risk_level, signal_count, risk_factors.
    Falls back to a rule-based formula if the LLM call fails.
    """
    if not signals:
        # No signals to assess — return default medium risk
        return json.dumps({
            "risk_score": 0.5,
            "risk_level": "medium",
            "signal_count": 0,
            "risk_factors": ["No signals available to assess — defaulting to medium risk"],
        })

    prompt = _build_prompt(signals, knowledge_chunks, account_data)

    try:
        raw_response = call_llm(
            prompt,
            max_tokens=1024,
            temperature=0,
            json_mode=True,
        )
        return raw_response
    except Exception:
        # Fallback: rule-based formula so the pipeline never breaks
        high_risk_count = sum(
            1 for s in signals
            if s.get("type") == "risk" and s.get("severity") == "high"
        )
        med_risk_count = sum(
            1 for s in signals
            if s.get("type") == "risk" and s.get("severity") == "medium"
        )
        positive_count = sum(1 for s in signals if s.get("type") == "positive")

        raw_score = 0.5 + (high_risk_count * 0.12) + (med_risk_count * 0.06) - (positive_count * 0.15)
        risk_score = max(0.0, min(1.0, raw_score))

        if risk_score >= 0.75:
            risk_level = "critical"
        elif risk_score >= 0.50:
            risk_level = "high"
        elif risk_score >= 0.25:
            risk_level = "medium"
        else:
            risk_level = "low"

        risk_factors = []
        if high_risk_count > 0:
            risk_factors.append(f"{high_risk_count} high-severity risk signal(s) detected")
        if med_risk_count > 0:
            risk_factors.append(f"{med_risk_count} medium-severity risk signal(s) detected")
        if positive_count > 0:
            risk_factors.append(f"{positive_count} positive signal(s) indicate customer satisfaction")

        return json.dumps({
            "risk_score": round(risk_score, 2),
            "risk_level": risk_level,
            "signal_count": max(len(signals), 1),
            "risk_factors": risk_factors or ["General risk factors present"],
        })


def _parse_risk_assessment(raw: str) -> dict:
    """Strip markdown fences and parse JSON risk assessment."""
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[-1]
        cleaned = cleaned.rsplit("```", 1)[0]
        cleaned = cleaned.strip()

    parsed = json.loads(cleaned)
    required = {"risk_score", "risk_level", "signal_count", "risk_factors"}
    if not all(k in parsed for k in required):
        raise ValueError(f"Missing required keys. Got: {list(parsed.keys())}")
    if parsed["risk_level"] not in ("critical", "high", "medium", "low"):
        raise ValueError(f"Invalid risk_level: {parsed['risk_level']}")
    return parsed


def _map_risk_factors_to_evidence(
    risk_factors: list, knowledge_chunks: list
) -> list:
    """
    Map each risk_factor string to the closest Evidence.id by substring
    matching against evidence excerpts.
    """
    if not knowledge_chunks:
        return ["" for _ in risk_factors]

    mapped = []
    for factor in risk_factors:
        factor_lower = factor.lower()
        matched = False
        for chunk in knowledge_chunks:
            excerpt = chunk.get("excerpt", "").lower()
            if any(word in excerpt for word in factor_lower.split()[:5]):
                mapped.append(chunk.get("id", knowledge_chunks[0].get("id", "")))
                matched = True
                break
        if not matched:
            mapped.append(knowledge_chunks[0].get("id", ""))
    return mapped


def assess(state: dict) -> dict:
    """
    Risk Assessor node: evaluates churn risk from signals + knowledge
    and produces a structured risk assessment with mapped evidence.
    """
    start = time.time()

    signals = state.get("signals", [])
    knowledge_chunks = state.get("knowledge_chunks", [])
    account_data = state.get("account_data", {})

    try:
        raw_response = _call_model(signals, knowledge_chunks, account_data)
        parsed = _parse_risk_assessment(raw_response)

        # Override signal_count with actual count if needed
        parsed["signal_count"] = max(parsed.get("signal_count", 0), len(signals))

        # Map risk factors to evidence IDs
        parsed["risk_factors"] = _map_risk_factors_to_evidence(
            parsed["risk_factors"], knowledge_chunks
        )

        risk_score = parsed["risk_score"]
        risk_level = parsed["risk_level"]
        reasoning = f"Risk level: {risk_level}, score: {risk_score:.2f}"

    except Exception as e:
        risk_score = 0.5
        risk_level = "medium"
        parsed = {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "signal_count": len(signals),
            "risk_factors": [""],
        }
        reasoning = f"Risk assessment failed: {str(e)}"

    duration_ms = max(1, round((time.time() - start) * 1000))

    step = {
        "agent_name": "risk_assessor",
        "action": "assessed_risk",
        "reasoning": reasoning,
        "duration_ms": duration_ms,
    }
    state["agent_trace"].append(step)

    return {"risk": parsed, "agent_trace": state["agent_trace"]}
