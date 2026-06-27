import json
import time
from typing import Optional

from backend.models.schemas import AgentStep


# ---------------------------------------------------------------------------
# Model abstraction — swap this out when your open-source model is ready
# ---------------------------------------------------------------------------
def _call_model(signals: list, knowledge_chunks: list) -> Optional[str]:
    """
    Stub: rule-based risk assessment so the pipeline runs end-to-end
    without a real model. Replace with your open-source model later.
    Uses structured signal data directly rather than parsing a prompt string.
    """
    # Count signals by type and severity
    high_risk_count = 0
    med_risk_count = 0
    low_risk_count = 0
    positive_count = 0
    neutral_count = 0

    for s in signals:
        signal_type = s.get("type", "")
        severity = s.get("severity", "")

        if signal_type == "positive":
            positive_count += 1
        elif signal_type == "neutral":
            neutral_count += 1
        elif signal_type == "risk":
            if severity == "high":
                high_risk_count += 1
            elif severity == "medium":
                med_risk_count += 1
            elif severity == "low":
                low_risk_count += 1

    total_signal_count = high_risk_count + med_risk_count + low_risk_count + positive_count + neutral_count

    # If no signals at all, default to medium (no information = moderate risk)
    if total_signal_count == 0:
        result = {
            "risk_score": 0.5,
            "risk_level": "medium",
            "signal_count": 0,
            "risk_factors": ["No signals available to assess — defaulting to medium risk"],
        }
        return json.dumps(result)

    # Weighted risk score calculation
    base_score = 0.5
    high_weight = 0.12
    med_weight = 0.06
    low_weight = 0.02
    positive_reduction = 0.15

    raw_score = (
        base_score
        + (high_risk_count * high_weight)
        + (med_risk_count * med_weight)
        - (positive_count * positive_reduction)
    )
    risk_score = max(0.0, min(1.0, raw_score))

    # Risk level classification
    if risk_score >= 0.75:
        risk_level = "critical"
    elif risk_score >= 0.50:
        risk_level = "high"
    elif risk_score >= 0.25:
        risk_level = "medium"
    else:
        risk_level = "low"

    # Build risk factors
    risk_factors = []
    if high_risk_count > 0:
        risk_factors.append(f"{high_risk_count} high-severity risk signal(s) detected")
    if med_risk_count > 0:
        risk_factors.append(f"{med_risk_count} medium-severity risk signal(s) detected")
    if low_risk_count > 0:
        risk_factors.append(f"{low_risk_count} low-severity risk signal(s) detected")
    if positive_count > 0:
        risk_factors.append(f"{positive_count} positive signal(s) indicate customer satisfaction")

    if not risk_factors:
        if risk_score < 0.25:
            risk_factors.append("No significant risk signals detected — account appears healthy")
        else:
            risk_factors.append("General risk factors present")

    result = {
        "risk_score": round(risk_score, 2),
        "risk_level": risk_level,
        "signal_count": max(total_signal_count, 1),
        "risk_factors": risk_factors,
    }

    return json.dumps(result)


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

    prompt = (
        "You are a customer success risk analyst. Given these signals and "
        "knowledge articles, assess churn risk.\n"
        "Return ONLY JSON: {\"risk_score\": float 0.0-1.0, "
        "\"risk_level\": \"critical|high|medium|low\", "
        "\"signal_count\": int, \"risk_factors\": [str]}\n\n"
        f"Signals:\n{json.dumps(signals, indent=2)}\n\n"
        f"Knowledge:\n{json.dumps(knowledge_chunks, indent=2)}"
    )

    try:
        raw_response = _call_model(signals, knowledge_chunks)
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
