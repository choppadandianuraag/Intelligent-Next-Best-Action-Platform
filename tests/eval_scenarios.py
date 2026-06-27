import pytest
from backend.agents.graph import run

SCENARIOS = [
    {
        "account_id": "test_account",
        "transcript": "VP is furious. 47 days to renewal. Zero adoption of reporting module. Explicit churn threat.",
        "expected_risk_level": "critical",
        "expected_keyword": "EBR",
    },
    {
        "account_id": "test_account",
        "transcript": "Power users love the product. Asking about enterprise tier and API access. Great NPS.",
        "expected_risk_level": "low",
        "expected_keyword": "enterprise",
    },
    {
        "account_id": "test_account",
        "transcript": "Customer is onboarding. One user mentioned they find the dashboard useful. They have standard setup questions about SSO configuration.",
        "expected_risk_level": "medium",
        "expected_keyword": "Quarterly Business Review",
    },
]


@pytest.mark.parametrize("scenario", SCENARIOS)
def test_scenario(scenario):
    result = run(scenario["transcript"], scenario["account_id"])
    assert result.risk_level == scenario["expected_risk_level"]
    assert scenario["expected_keyword"].lower() in result.primary_recommendation.title.lower()
