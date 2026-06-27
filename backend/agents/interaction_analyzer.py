"""
Interaction Analyzer agent.

Extracts structured signals (risk, positive, neutral) from a raw meeting
transcript using an LLM (Groq via OpenAI-compatible client).
This is the first specialist agent in the LangGraph pipeline.
"""

import json
import time
from typing import List, Dict

from backend.agents.llm_client import call_llm

VALID_TYPES = {"risk", "positive", "neutral"}
VALID_SEVERITIES = {"high", "medium", "low"}


def _build_prompt(transcript: str) -> str:
    """Build the LLM prompt for signal extraction."""
    return (
        "You are a customer success signal extractor. Read the following meeting transcript "
        "and extract all meaningful signals.\n"
        "For each signal, return: text (exact quote or paraphrase), "
        "type (risk, positive, or neutral), severity (high, medium, low).\n"
        "Return ONLY a JSON list. No markdown fences.\n\n"
        f"Transcript:\n{transcript}"
    )


def _strip_fences(raw: str) -> str:
    """Strip markdown code fences from the response string."""
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        lines = cleaned.split("\n", 1)
        if len(lines) > 1:
            cleaned = lines[1]
        # Remove trailing fence
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        elif "```" in cleaned:
            cleaned = cleaned.rsplit("```", 1)[0]
        cleaned = cleaned.strip()
    return cleaned


def _validate_signals(signals: list) -> List[Dict]:
    """
    Validate that signals is a list of dicts with the required keys
    and valid values.
    """
    if not isinstance(signals, list):
        raise ValueError("Response is not a JSON list")

    validated = []
    for item in signals:
        if not isinstance(item, dict):
            raise ValueError(f"Signal is not a dict: {item}")
        if "text" not in item:
            raise ValueError(f"Signal missing 'text' key: {item}")
        if "type" not in item:
            raise ValueError(f"Signal missing 'type' key: {item}")
        if "severity" not in item:
            raise ValueError(f"Signal missing 'severity' key: {item}")
        if item["type"] not in VALID_TYPES:
            raise ValueError(
                f"Invalid signal type '{item['type']}'. Must be one of {VALID_TYPES}"
            )
        if item["severity"] not in VALID_SEVERITIES:
            raise ValueError(
                f"Invalid severity '{item['severity']}'. Must be one of {VALID_SEVERITIES}"
            )
        validated.append(item)

    return validated


def analyze(state: dict) -> dict:
    """
    Interaction Analyzer node: extracts risk/positive/neutral signals
    from the meeting transcript and stores them in state['signals'].

    Args:
        state: LangGraph state dict containing 'raw_input' (the transcript).

    Returns:
        Dict with 'signals' (list of signal dicts) and 'agent_trace' (updated).
    """
    start = time.time()

    transcript = state.get("raw_input", "")
    prompt = _build_prompt(transcript)

    signals = []
    action = "extracted_signals"
    reasoning = ""

    try:
        raw_response = call_llm(prompt, max_tokens=1024, temperature=0)
        cleaned = _strip_fences(raw_response)
        parsed = json.loads(cleaned)
        signals = _validate_signals(parsed)
        reasoning = f"Found {len(signals)} signals"
    except Exception as e:
        signals = []
        action = "extraction_failed"
        reasoning = f"Extraction failed: {str(e)}"

    duration_ms = max(1, int((time.time() - start) * 1000))

    state["agent_trace"].append({
        "agent_name": "interaction_analyzer",
        "action": action,
        "reasoning": reasoning,
        "duration_ms": duration_ms,
    })

    return {"signals": signals, "agent_trace": state["agent_trace"]}
