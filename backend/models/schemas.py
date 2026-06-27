"""
Pydantic v2 schemas — the shared contract between all Meridian components.
"""
from __future__ import annotations

from datetime import datetime
from typing import List, Literal, Optional
from pydantic import BaseModel, Field
import uuid


# ---------------------------------------------------------------------------
# Agent pipeline models
# ---------------------------------------------------------------------------

class AgentStep(BaseModel):
    agent_name: str
    action: str
    reasoning: str
    duration_ms: int


class Evidence(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_type: Literal["meeting_note", "playbook", "memory", "crm"]
    source_name: str
    excerpt: str
    relevance_score: float = Field(ge=0.0, le=1.0)


class Action(BaseModel):
    title: str
    description: str
    confidence: float = Field(ge=0.0, le=1.0)
    estimated_impact: str
    evidence_ids: List[str] = Field(default_factory=list)
    precedent_accounts: List[str] = Field(default_factory=list)


class MemoryContext(BaseModel):
    similar_cases_found: int
    confidence_boost: float
    base_confidence: float
    boosted_confidence: float
    precedent_accounts: List[str] = Field(default_factory=list)


class RecommendationOutput(BaseModel):
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    account_name: str
    csm_name: str
    renewal_date: str
    risk_score: float = Field(ge=0.0, le=1.0)
    risk_level: Literal["critical", "high", "medium", "low"]
    signal_count: int
    agent_trace: List[AgentStep]
    evidence: List[Evidence]
    primary_recommendation: Action
    alternatives: List[Action]
    memory_context: Optional[MemoryContext] = None
    generated_at: datetime = Field(default_factory=datetime.utcnow)


# ---------------------------------------------------------------------------
# LangGraph state
# ---------------------------------------------------------------------------

class GraphState(BaseModel):
    """Typed state dict passed through the LangGraph pipeline."""
    raw_input: str = ""
    account_id: str = ""
    signals: List[dict] = Field(default_factory=list)
    knowledge_chunks: List[dict] = Field(default_factory=list)
    risk: dict = Field(default_factory=dict)
    recommendations: dict = Field(default_factory=dict)
    agent_trace: List[dict] = Field(default_factory=list)
    memory_context: Optional[dict] = None
    customer_profile: Optional[dict] = None


# ---------------------------------------------------------------------------
# API request/response bodies
# ---------------------------------------------------------------------------

class AnalyzeRequest(BaseModel):
    account_id: str
    interaction_text: str


class FeedbackRequest(BaseModel):
    request_id: str
    decision: Literal["accepted", "modified", "rejected"]
    modification_notes: Optional[str] = None
