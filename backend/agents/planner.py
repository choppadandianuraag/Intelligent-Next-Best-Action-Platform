"""
Planner agent — reads raw_input, logs an AgentStep, and sets the execution_plan.
Always schedules all 4 specialist agents in fixed order.
"""
import time
from backend.models.schemas import AgentStep


EXECUTION_PLAN = [
    "interaction_analyzer",
    "knowledge_retriever",
    "risk_assessor",
    "nba_generator",
]


def planner_node(state: dict) -> dict:
    start = time.time()

    account_id = state.get("account_id", "unknown")
    raw_input = state.get("raw_input", "")
    word_count = len(raw_input.split())

    reasoning = (
        f"Received interaction text ({word_count} words) for account '{account_id}'. "
        f"Scheduling all 4 specialist agents in standard order: "
        f"{', '.join(EXECUTION_PLAN)}."
    )

    duration_ms = int((time.time() - start) * 1000)

    step = AgentStep(
        agent_name="Planner",
        action=f"Parsed input and created execution plan for account '{account_id}'",
        reasoning=reasoning,
        duration_ms=max(duration_ms, 1),
    )

    agent_trace = state.get("agent_trace", [])
    agent_trace.append(step.model_dump())

    return {
        **state,
        "agent_trace": agent_trace,
        "execution_plan": EXECUTION_PLAN,
    }
