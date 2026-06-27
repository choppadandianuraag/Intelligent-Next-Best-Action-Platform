import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from backend.models.schemas import AgentStep, Evidence, Action, MemoryContext, RecommendationOutput
from backend.agents.graph import run

# Test 1: Schema imports
print("[PASS] Schemas import OK")

# Test 2: Graph runs with dummy data
result = run(
    raw_input="Customer is angry about pricing and mentioned they are evaluating competitors. Renewal is in 30 days.",
    account_id="test_account"
)
assert isinstance(result, RecommendationOutput), "run() must return RecommendationOutput"
assert result.request_id and len(result.request_id) == 12
assert result.risk_score >= 0.0 and result.risk_score <= 1.0
assert result.risk_level in ["critical", "high", "medium", "low"]
assert len(result.agent_trace) >= 5, f"Expected >=5 agent steps, got {len(result.agent_trace)}"
assert all(isinstance(s, AgentStep) for s in result.agent_trace)
assert all(s.duration_ms > 0 for s in result.agent_trace)
assert result.primary_recommendation is not None
assert len(result.alternatives) == 2
print("[PASS] End-to-end graph execution OK")
print("[PASS] All P1 verification checks passed.")
