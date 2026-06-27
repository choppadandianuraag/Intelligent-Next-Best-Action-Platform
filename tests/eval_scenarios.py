"""
5-case evaluation suite for Meridian.
Run: pytest tests/eval_scenarios.py -v

NOTE: Requires the backend to be running and ChromaDB + episodic memory seeded.
Set ANTHROPIC_API_KEY in .env before running.
"""
import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.agents.graph import run

# ---------------------------------------------------------------------------
# Load actual transcript content for eval
# ---------------------------------------------------------------------------

def _load_transcript(filename: str) -> str:
    path = os.path.join("backend", "data", "meeting_notes", filename)
    with open(path, encoding="utf-8") as f:
        return f.read()


SCENARIOS = [
    {
        "name": "Acme Corp — Critical churn risk",
        "account_id": "acme_corp",
        "transcript": _load_transcript("acme_corp.md"),
        "expected_risk_level": "critical",
        "expected_primary_action_keyword": "EBR",
    },
    {
        "name": "Globex Corp — Expansion opportunity",
        "account_id": "globex_corp",
        "transcript": _load_transcript("globex_corp.md"),
        "expected_risk_level": "low",
        "expected_primary_action_keyword": "enterprise",
    },
    {
        "name": "TechCorp — Onboarding friction",
        "account_id": "techcorp",
        "transcript": _load_transcript("techcorp.md"),
        "expected_risk_level": "medium",
        "expected_primary_action_keyword": "onboarding",
    },
    {
        "name": "Nexus Systems — Champion departure critical",
        "account_id": "nexus_systems",
        "transcript": _load_transcript("nexus_systems.md"),
        "expected_risk_level": "critical",
        "expected_primary_action_keyword": "champion",
    },
    {
        "name": "Umbrella Corp — Healthy expansion",
        "account_id": "umbrella_corp",
        "transcript": _load_transcript("umbrella_corp.md"),
        "expected_risk_level": "low",
        "expected_primary_action_keyword": "expansion",
    },
]


@pytest.mark.parametrize("scenario", SCENARIOS, ids=[s["name"] for s in SCENARIOS])
def test_scenario(scenario):
    result = run(scenario["transcript"], scenario["account_id"])

    assert result is not None, "run() returned None"
    assert result.risk_level == scenario["expected_risk_level"], (
        f"Expected risk_level={scenario['expected_risk_level']!r}, "
        f"got {result.risk_level!r}"
    )

    keyword = scenario["expected_primary_action_keyword"].lower()
    title_lower = result.primary_recommendation.title.lower()
    desc_lower = result.primary_recommendation.description.lower()
    assert keyword in title_lower or keyword in desc_lower, (
        f"Expected keyword {keyword!r} in primary recommendation, "
        f"got title={result.primary_recommendation.title!r}"
    )

    # Basic structural checks
    assert len(result.agent_trace) >= 4, "Expected at least 4 agent steps in trace"
    assert len(result.alternatives) >= 2, "Expected at least 2 alternative actions"
    assert 0.0 <= result.risk_score <= 1.0, "Risk score out of range"
