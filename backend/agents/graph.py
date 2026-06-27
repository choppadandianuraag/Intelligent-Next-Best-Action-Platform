"""
LangGraph StateGraph — wires all 5 agents in sequence.

Pipeline: START → planner → interaction_analyzer → knowledge_retriever → risk_assessor → nba_generator → END

The run() function is the public entry point called by FastAPI and the eval suite.
"""
import json
import os
import uuid
from datetime import datetime
from typing import Any

from langgraph.graph import StateGraph, END
from dotenv import load_dotenv

from backend.agents.planner import planner_node
from backend.agents.interaction_analyzer import interaction_analyzer_node
from backend.agents.knowledge_retriever import knowledge_retriever_node
from backend.agents.risk_assessor import risk_assessor_node
from backend.agents.nba_generator import nba_generator_node
from backend.models.schemas import (
    Action,
    AgentStep,
    Evidence,
    MemoryContext,
    RecommendationOutput,
)

load_dotenv()

# ---------------------------------------------------------------------------
# Build the graph
# ---------------------------------------------------------------------------

def _build_graph():
    g = StateGraph(dict)
    g.add_node("planner", planner_node)
    g.add_node("interaction_analyzer", interaction_analyzer_node)
    g.add_node("knowledge_retriever", knowledge_retriever_node)
    g.add_node("risk_assessor", risk_assessor_node)
    g.add_node("nba_generator", nba_generator_node)

    g.set_entry_point("planner")
    g.add_edge("planner", "interaction_analyzer")
    g.add_edge("interaction_analyzer", "knowledge_retriever")
    g.add_edge("knowledge_retriever", "risk_assessor")
    g.add_edge("risk_assessor", "nba_generator")
    g.add_edge("nba_generator", END)

    return g.compile()


_graph = _build_graph()


# ---------------------------------------------------------------------------
# Load customer profile helper
# ---------------------------------------------------------------------------

def _load_profile(account_id: str) -> dict:
    path = os.path.join("backend", "data", "customer_profiles", f"{account_id}.json")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return {}


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def run(interaction_text: str, account_id: str) -> RecommendationOutput:
    """Run the full agent pipeline and return a RecommendationOutput."""
    profile = _load_profile(account_id)

    initial_state = {
        "raw_input": interaction_text,
        "account_id": account_id,
        "signals": [],
        "knowledge_chunks": [],
        "risk": {},
        "recommendations": {},
        "agent_trace": [],
        "memory_context": None,
        "customer_profile": profile,
    }

    final_state = _graph.invoke(initial_state)

    # --- Assemble output ---
    risk = final_state.get("risk", {})
    recs = final_state.get("recommendations", {})
    memory_ctx_raw = final_state.get("memory_context")
    trace_raw = final_state.get("agent_trace", [])
    evidence_raw = final_state.get("knowledge_chunks", [])

    agent_trace = [AgentStep(**s) for s in trace_raw]
    evidence = [Evidence(**e) for e in evidence_raw]

    primary_raw = recs.get("primary", {})
    primary = Action(
        title=primary_raw.get("title", "Review account"),
        description=primary_raw.get("description", ""),
        confidence=float(primary_raw.get("confidence", 0.73)),
        estimated_impact=primary_raw.get("estimated_impact", "Unknown"),
        evidence_ids=primary_raw.get("evidence_ids", []),
        precedent_accounts=primary_raw.get("precedent_accounts", []),
    )

    alternatives = []
    for alt_raw in recs.get("alternatives", [])[:2]:
        alternatives.append(
            Action(
                title=alt_raw.get("title", "Alternative action"),
                description=alt_raw.get("description", ""),
                confidence=float(alt_raw.get("confidence", 0.5)),
                estimated_impact=alt_raw.get("estimated_impact", "Medium"),
                evidence_ids=alt_raw.get("evidence_ids", []),
                precedent_accounts=alt_raw.get("precedent_accounts", []),
            )
        )

    memory_context = MemoryContext(**memory_ctx_raw) if memory_ctx_raw else None

    risk_score = float(risk.get("score", 0.5))
    risk_level = risk.get("level", "medium")

    return RecommendationOutput(
        request_id=str(uuid.uuid4()),
        account_name=profile.get("account_name", account_id),
        csm_name=profile.get("csm", "Unknown CSM"),
        renewal_date=profile.get("contract_end", "Unknown"),
        risk_score=risk_score,
        risk_level=risk_level,
        signal_count=risk.get("signal_count", len(final_state.get("signals", []))),
        agent_trace=agent_trace,
        evidence=evidence,
        primary_recommendation=primary,
        alternatives=alternatives,
        memory_context=memory_context,
        generated_at=datetime.utcnow(),
    )
