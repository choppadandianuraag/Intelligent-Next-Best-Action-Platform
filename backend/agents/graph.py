import json
import os
import uuid
from datetime import datetime
from typing import TypedDict, List, Optional

from langgraph.graph import StateGraph, END

from backend.models.schemas import (
    AgentStep,
    Evidence,
    Action,
    RecommendationOutput,
)
from backend.agents.planner import plan
from backend.agents.interaction_analyzer import analyze
from backend.agents.knowledge_retriever import retrieve
from backend.agents.risk_assessor import assess
from backend.agents.nba_generator import generate


class GraphState(TypedDict):
    raw_input: str
    account_id: str
    signals: List[dict]
    knowledge_chunks: List[dict]
    risk: dict
    recommendations: dict
    agent_trace: List[dict]
    account_data: dict
    execution_plan: Optional[List[str]]


builder = StateGraph(GraphState)

builder.add_node("planner", plan)
builder.add_node("interaction_analyzer", analyze)
builder.add_node("knowledge_retriever", retrieve)
builder.add_node("risk_assessor", assess)
builder.add_node("nba_generator", generate)

builder.set_entry_point("planner")
builder.add_edge("planner", "interaction_analyzer")
builder.add_edge("interaction_analyzer", "knowledge_retriever")
builder.add_edge("knowledge_retriever", "risk_assessor")
builder.add_edge("risk_assessor", "nba_generator")
builder.add_edge("nba_generator", END)

graph = builder.compile()


def _load_profile(account_id: str) -> dict:
    base_dir = os.path.join(os.path.dirname(__file__), "..", "data", "customer_profiles")
    path = os.path.join(base_dir, f"{account_id}.json")
    try:
        with open(path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {
            "account_name": account_id,
            "arr": 0,
            "industry": "Unknown",
            "contract_end": "N/A",
            "csm": "Unknown",
            "health_score_history": [],
            "daily_active_users": 0,
            "last_login_date": "N/A",
            "features_adopted": [],
            "open_tickets": 0,
            "nps_score": 0,
        }


def run(raw_input: str, account_id: str) -> RecommendationOutput:
    """
    Execute the full Meridian agent pipeline end-to-end.

    Args:
        raw_input: The meeting transcript text to analyze.
        account_id: The customer account identifier (used to load profile).

    Returns:
        A fully populated RecommendationOutput with risk assessment,
        evidence, recommendations, and agent trace.
    """
    profile = _load_profile(account_id)

    initial_state: GraphState = {
        "raw_input": raw_input,
        "account_id": account_id,
        "signals": [],
        "knowledge_chunks": [],
        "risk": {},
        "recommendations": {},
        "agent_trace": [],
        "account_data": profile,
        "execution_plan": None,
    }

    final_state = graph.invoke(initial_state)

    agent_trace = [AgentStep(**s) for s in final_state["agent_trace"]]
    evidence_raw = final_state.get("knowledge_chunks", [])
    evidence = [Evidence(**e) if isinstance(e, dict) else e for e in evidence_raw]
    recs = final_state.get("recommendations", {})
    primary = Action(**recs.get("primary", {}))
    alternatives = [Action(**a) if isinstance(a, dict) else a for a in recs.get("alternatives", [])]

    return RecommendationOutput(
        request_id=uuid.uuid4().hex[:12],
        account_name=profile.get("account_name", account_id),
        csm_name=profile.get("csm", "Unknown"),
        renewal_date=profile.get("contract_end", "N/A"),
        risk_score=final_state["risk"].get("risk_score", 0.0),
        risk_level=final_state["risk"].get("risk_level", "medium"),
        signal_count=final_state["risk"].get("signal_count", 0),
        agent_trace=agent_trace,
        evidence=evidence,
        primary_recommendation=primary,
        alternatives=alternatives,
        memory_context=None,
        generated_at=datetime.utcnow(),
    )
