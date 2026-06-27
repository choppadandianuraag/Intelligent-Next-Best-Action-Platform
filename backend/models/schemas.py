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
    memory_context: Optional[MemoryContext] = None
    generated_at: datetime
