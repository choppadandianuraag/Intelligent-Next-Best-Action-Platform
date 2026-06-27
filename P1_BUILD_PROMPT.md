You are an expert Python backend engineer building the AI agent layer for "Meridian", a decision-intelligence system for customer-success teams.

YOUR GOAL: Write the complete, production-ready P1 codebase. Every function must be fully implemented. No TODOs. No placeholders. The code must run end-to-end with a dummy transcript when you are done.

TECH STACK: Python 3.11, LangGraph, Anthropic Claude API, Pydantic v2, python-dotenv.

CRITICAL RULES:
1. Work inside the `meridian/` repo root. Create all files under `backend/`.
2. Use EXACT class names, field names, and function signatures shown below. Never rename them.
3. Read the Anthropic API key from `os.getenv("ANTHROPIC_API_KEY")`. Fail loudly if it is missing.
4. Every agent node must measure `duration_ms` with `time.time()`, round to int, and append an `AgentStep` dict to `state["agent_trace"]`.
5. If a dependency owned by P2 does not exist yet, create a minimal stub with the exact same interface so imports succeed.
6. After each Day, run the provided verification script and fix errors until it passes.

---

## STEP 1: Create `backend/models/schemas.py`

This is the immutable contract. Write exactly:

```python
from pydantic import BaseModel
from typing import List, Optional, Literal
from datetime import datetime

class AgentStep(BaseModel):
    agent_name: str
    action: str
    reasoning: str
    duration_ms: int

class Evidence(BaseModel):
    id: str
    source_type: Literal["meeting_note", "playbook", "memory", "crm"]
    source_name: str
    excerpt: str
    relevance_score: float

class Action(BaseModel):
    title: str
    description: str
    confidence: float
    estimated_impact: str
    evidence_ids: List[str]
    precedent_accounts: List[str]

class MemoryContext(BaseModel):
    similar_cases_found: int
    confidence_boost: float
    base_confidence: float
    boosted_confidence: float
    precedent_accounts: List[str]

class RecommendationOutput(BaseModel):
    request_id: str
    account_name: str
    csm_name: str
    renewal_date: str
    risk_score: float
    risk_level: Literal["critical", "high", "medium", "low"]
    signal_count: int
    agent_trace: List[AgentStep]
    evidence: List[Evidence]
    primary_recommendation: Action
    alternatives: List[Action]
    memory_context: Optional[MemoryContext]
    generated_at: datetime
```

---

## STEP 2: Create P2 stubs so P1 can run independently

Create `backend/memory/vector_store.py`:

```python
from typing import List, Dict

class VectorStore:
    def search(self, query: str, collection: str, n: int = 5) -> List[Dict]:
        # Stub: returns fake results so the pipeline never breaks
        return [
            {"id": f"stub_{i}", "excerpt": f"Stub knowledge about {query[:20]}...", "metadata": {"source_file": "stub.md"}, "distance": 0.5}
            for i in range(min(n, 2))
        ]
```

Create `backend/memory/episodic.py`:

```python
from backend.models.schemas import MemoryContext

class EpisodicMemory:
    def get_memory_context(self, risk_level: str, risk_score: float) -> MemoryContext:
        # Stub: no memory on cold start
        return MemoryContext(
            similar_cases_found=0,
            confidence_boost=0.0,
            base_confidence=0.73,
            boosted_confidence=0.73,
            precedent_accounts=[]
        )
```

Create a dummy customer profile for testing at `backend/data/customer_profiles/test_account.json`:

```json
{
  "account_name": "Test Account",
  "arr": 100000,
  "industry": "Software",
  "contract_end": "2026-12-31",
  "csm": "Alex Smith",
  "health_score_history": [80, 75, 70],
  "daily_active_users": 50,
  "last_login_date": "2026-06-25",
  "features_adopted": ["dashboard"],
  "open_tickets": 3,
  "nps_score": 45
}
```

---

## STEP 3: Create `backend/agents/planner.py`

Logic:
- Input: `state` dict.
- Record start time.
- Build `execution_plan = ["interaction_analyzer", "knowledge_retriever", "risk_assessor", "nba_generator"]`.
- Build `AgentStep(agent_name="planner", action="created_execution_plan", reasoning="Standard 4-agent pipeline for customer success analysis", duration_ms=...)`. Compute duration.
- Append step to `state["agent_trace"]`.
- Return `{"execution_plan": execution_plan, "agent_trace": state["agent_trace"]}`.

---

## STEP 4: Create `backend/agents/interaction_analyzer.py`

Logic:
- Import `anthropic`, `os`, `json`, `time`.
- Instantiate `anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))`.
- Node function `analyze(state)`:
  1. Record start time.
  2. Read `state["raw_input"]`.
  3. Call Claude with this exact prompt template:
     ```
     You are a customer success signal extractor. Read the following meeting transcript and extract all meaningful signals.
     For each signal, return: text (exact quote or paraphrase), type (risk, positive, or neutral), severity (high, medium, low).
     Return ONLY a JSON list. No markdown fences.

     Transcript:
     {transcript}
     ```
  4. Use model `claude-3-5-sonnet-latest`, `max_tokens=1024`, `temperature=0`.
  5. Strip any markdown fences (` ```json ... ``` `) from the response content.
  6. Parse the cleaned string with `json.loads()`.
  7. Validate that it is a list of dicts with keys `text`, `type`, `severity`.
  8. Record end time. Build `AgentStep(agent_name="interaction_analyzer", action="extracted_signals", reasoning=f"Found {len(signals)} signals", duration_ms=...)`. Append to trace.
  9. Return `{"signals": signals, "agent_trace": state["agent_trace"]}`.
- If Claude returns invalid JSON, catch the exception, log a step with `action="extraction_failed"`, and return `{"signals": [], "agent_trace": ...}` so the graph does not crash.

---

## STEP 5: Create `backend/agents/knowledge_retriever.py`

Logic:
- Import `backend.memory.vector_store`.
- Node function `retrieve(state)`:
  1. Record start time.
  2. Instantiate `VectorStore()`.
  3. For each signal in `state["signals"]`, call `store.search(query=signal["text"], collection="knowledge_base", n=5)`.
  4. Deduplicate results by `(metadata["source_file"], excerpt[:100])`.
  6. Build `Evidence` objects. Assign `id = f"ev_{index}"` sequentially. Compute `relevance_score = 1.0 - (distance / 2.0)` capped to `[0.0, 1.0]` (distance comes from ChromaDB; stub uses 0.5 so score becomes 0.75).
  7. Store list in `state["knowledge_chunks"]`.
  8. Log `AgentStep(agent_name="knowledge_retriever", action="retrieved_knowledge", reasoning=f"Found {len(evidence)} unique chunks from knowledge base", duration_ms=...)`.
  9. Return `{"knowledge_chunks": evidence, "agent_trace": state["agent_trace"]}`.

---

## STEP 6: Create `backend/agents/risk_assessor.py`

Logic:
- Node function `assess(state)`:
  1. Record start time.
  2. Build prompt string:
     ```
     You are a customer success risk analyst. Given these signals and knowledge articles, assess churn risk.
     Return ONLY JSON: {"risk_score": float 0.0-1.0, "risk_level": "critical|high|medium|low", "signal_count": int, "risk_factors": [str]}

     Signals:
     {signals}

     Knowledge:
     {knowledge_chunks}
     ```
  3. Call Claude (same client setup as interaction_analyzer) with `claude-3-5-sonnet-latest`, `max_tokens=512`, `temperature=0`.
  4. Strip markdown fences. Parse JSON.
  5. Validate keys exist. `signal_count` should equal `len(state["signals"])` if possible; if not, overwrite it with the actual count.
  6. Map each `risk_factor` string to the closest `Evidence.id` by simple substring matching against evidence excerpts. If no match, map to first evidence ID or empty string.
  7. Log `AgentStep(agent_name="risk_assessor", action="assessed_risk", reasoning=f"Risk level: {risk_level}, score: {risk_score:.2f}", duration_ms=...)`.
  8. Return `{"risk": {"risk_score": ..., "risk_level": ..., "signal_count": ..., "risk_factors": [...]}, "agent_trace": state["agent_trace"]}`.
- Wrap in try/except. On failure, return `risk_score=0.5`, `risk_level="medium"`, empty factors, and log failure.

---

## STEP 7: Create `backend/agents/nba_generator.py`

Logic:
- Import `backend.memory.episodic`.
- Node function `generate(state)`:
  1. Record start time.
  2. Call `EpisodicMemory().get_memory_context(risk_level=state["risk"]["risk_level"], risk_score=state["risk"]["risk_score"])`.
  3. Build prompt:
     ```
     You are a customer success strategist. Given the risk assessment, knowledge, and past resolved cases, recommend 3 actions.
     Return ONLY JSON with keys: primary (Action), alternatives (list of 2 Actions).
     Action schema: {title, description, confidence (0.0-1.0), estimated_impact, evidence_ids, precedent_accounts}

     Risk: {risk}
     Knowledge: {knowledge}
     Memory: {memory_context}
     ```
  4. Call Claude with `claude-3-5-sonnet-latest`, `max_tokens=1024`, `temperature=0`.
  5. Strip fences. Parse JSON.
  6. Extract `primary` and `alternatives`.
  7. Apply confidence boost formula EXACTLY:
     ```python
     base_confidence = primary["confidence"]
     similar_count = memory_context.similar_cases_found
     boosted = min(base_confidence * (1 + 0.06 * similar_count), 0.97)
     primary["confidence"] = round(boosted, 3)
     primary["precedent_accounts"] = memory_context.precedent_accounts
     for alt in alternatives:
         alt["precedent_accounts"] = memory_context.precedent_accounts
     ```
  8. Log `AgentStep(agent_name="nba_generator", action="generated_recommendations", reasoning=f"Primary: {primary['title']}, confidence: {primary['confidence']}", duration_ms=...)`.
  9. Return `{"recommendations": {"primary": primary, "alternatives": alternatives}, "agent_trace": state["agent_trace"]}`.
- On failure, return a safe fallback primary action with title="Schedule follow-up call", confidence=0.5, etc.

---

## STEP 8: Create `backend/agents/graph.py`

Logic:
- Import `TypedDict` from `typing`, `StateGraph`, `END` from `langgraph.graph`.
- Define `GraphState(TypedDict)` with keys: `raw_input`, `account_id`, `signals`, `knowledge_chunks`, `risk`, `recommendations`, `agent_trace`, `account_data`.
- Build graph:
  ```python
  builder = StateGraph(GraphState)
  builder.add_node("planner", planner.plan)
  builder.add_node("interaction_analyzer", interaction_analyzer.analyze)
  builder.add_node("knowledge_retriever", knowledge_retriever.retrieve)
  builder.add_node("risk_assessor", risk_assessor.assess)
  builder.add_node("nba_generator", nba_generator.generate)
  builder.set_entry_point("planner")
  builder.add_edge("planner", "interaction_analyzer")
  builder.add_edge("interaction_analyzer", "knowledge_retriever")
  builder.add_edge("knowledge_retriever", "risk_assessor")
  builder.add_edge("risk_assessor", "nba_generator")
  builder.add_edge("nba_generator", END)
  graph = builder.compile()
  ```
- Expose `run(raw_input: str, account_id: str) -> RecommendationOutput`:
  1. Load profile from `backend/data/customer_profiles/{account_id}.json`. If missing, use fallback dict.
  2. Build initial state:
     ```python
     initial_state = {
         "raw_input": raw_input,
         "account_id": account_id,
         "signals": [],
         "knowledge_chunks": [],
         "risk": {},
         "recommendations": {},
         "agent_trace": [],
         "account_data": profile,
     }
     ```
  3. Invoke: `final_state = graph.invoke(initial_state)`.
  4. Extract data:
     - `request_id = uuid.uuid4().hex[:12]`
     - `account_name = profile.get("account_name", account_id)`
     - `csm_name = profile.get("csm", "Unknown")`
     - `renewal_date = profile.get("contract_end", "N/A")`
     - `risk_score = final_state["risk"].get("risk_score", 0.0)`
     - `risk_level = final_state["risk"].get("risk_level", "medium")`
     - `signal_count = final_state["risk"].get("signal_count", 0)`
     - `agent_trace = [AgentStep(**s) for s in final_state["agent_trace"]]`
     - `evidence = [Evidence(**e) for e in final_state["knowledge_chunks"]]`
     - `primary = Action(**final_state["recommendations"]["primary"])`
     - `alternatives = [Action(**a) for a in final_state["recommendations"].get("alternatives", [])]`
     - `memory_context = final_state.get("memory_context")` -- if present, wrap in `MemoryContext(**...)`, else `None`.
  5. Return `RecommendationOutput(..., generated_at=datetime.utcnow())`.

---

## STEP 9: Create `scripts/verify_p1.py`

After all files are written, create and run this verification script. It must pass with zero errors.

```python
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
```

Run it with:
```bash
python scripts/verify_p1.py
```

If any assertion fails, fix the corresponding agent until it passes.

---

## STEP 10: Day 3 tuning (only after verify_p1.py passes)

Create `tests/eval_scenarios.py` with these 3 scenarios. Do not paste full transcripts; use the short dummy transcripts provided below. The goal is structural correctness, not perfect demo scores yet.

```python
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
]

@pytest.mark.parametrize("scenario", SCENARIOS)
def test_scenario(scenario):
    result = run(scenario["transcript"], scenario["account_id"])
    assert result.risk_level == scenario["expected_risk_level"]
    assert scenario["expected_keyword"].lower() in result.primary_recommendation.title.lower()
```

Run `pytest tests/eval_scenarios.py -v`. If a scenario fails because Claude returns an unexpected keyword, adjust the prompt in the corresponding agent (NOT the schema) until it passes. You may add one sentence of instruction to the Claude prompt, e.g. "If risk is critical, the primary action should involve an Executive Business Review (EBR)."

---

## FINAL DELIVERABLE CHECKLIST

Before you finish, confirm:
- [ ] `backend/models/schemas.py` exists and imports cleanly.
- [ ] `backend/agents/graph.py` exposes `run(raw_input, account_id) -> RecommendationOutput`.
- [ ] `backend/agents/planner.py`, `interaction_analyzer.py`, `knowledge_retriever.py`, `risk_assessor.py`, `nba_generator.py` all exist and are fully implemented.
- [ ] Every agent appends an `AgentStep` with a valid `duration_ms > 0`.
- [ ] `python scripts/verify_p1.py` prints all PASS messages.
- [ ] `pytest tests/eval_scenarios.py` passes.
- [ ] No API keys are hardcoded.
- [ ] All files use relative imports from `backend.*`.
