"""
Interaction Analyzer agent — prompts Claude to extract signals from transcript.
Returns signals: list[dict] each with text, type (risk|positive|neutral), severity (high|medium|low).
"""
import json
import os
import time

import anthropic
from dotenv import load_dotenv

from backend.models.schemas import AgentStep

load_dotenv()

MODEL = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
_client = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    return _client


SYSTEM_PROMPT = """You are an expert customer success analyst. Your job is to extract signals from a customer meeting transcript.

Analyze the transcript and return a JSON array of signals. Each signal must have:
- "text": a concise description of the signal (1-2 sentences)
- "type": one of "risk", "positive", "neutral"
- "severity": one of "high", "medium", "low"

Focus on:
- Churn threats, competitor mentions, ROI questions (risk/high)
- Support ticket complaints, adoption gaps (risk/medium)
- Positive sentiment, expansion interest, NPS mentions (positive)
- Champion changes, executive engagement or disengagement (varies)

Return ONLY a valid JSON array. No explanation, no markdown fences."""


def interaction_analyzer_node(state: dict) -> dict:
    start = time.time()
    raw_input = state.get("raw_input", "")

    prompt = f"Extract signals from this customer meeting transcript:\n\n{raw_input}"

    try:
        response = _get_client().messages.create(
            model=MODEL,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )
        content = response.content[0].text.strip()
        # Strip markdown fences if present
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        signals = json.loads(content)
    except Exception as e:
        signals = [
            {
                "text": f"Signal extraction failed: {str(e)}",
                "type": "neutral",
                "severity": "low",
            }
        ]

    duration_ms = int((time.time() - start) * 1000)

    step = AgentStep(
        agent_name="Interaction Analyzer",
        action=f"Extracted {len(signals)} signals from transcript",
        reasoning=(
            f"Analyzed {len(raw_input.split())} words of transcript. "
            f"Found {sum(1 for s in signals if s.get('type') == 'risk')} risk signals, "
            f"{sum(1 for s in signals if s.get('type') == 'positive')} positive signals."
        ),
        duration_ms=duration_ms,
    )

    agent_trace = state.get("agent_trace", [])
    agent_trace.append(step.model_dump())

    return {**state, "signals": signals, "agent_trace": agent_trace}
