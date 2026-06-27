import time
from backend.models.schemas import AgentStep


def plan(state: dict) -> dict:
    """
    Planner node: builds the execution plan and logs the first agent step.
    Always invokes all 3 specialist agents in sequence.
    """
    start = time.time()

    execution_plan = [
        "interaction_analyzer",
        "knowledge_retriever",
        "risk_assessor",
        "nba_generator",
    ]

    duration_ms = max(1, round((time.time() - start) * 1000))

    step = AgentStep(
        agent_name="planner",
        action="created_execution_plan",
        reasoning="Standard 4-agent pipeline for customer success analysis",
        duration_ms=duration_ms,
        )

    state["agent_trace"].append(step.model_dump())

    return {"execution_plan": execution_plan, "agent_trace": state["agent_trace"]}
