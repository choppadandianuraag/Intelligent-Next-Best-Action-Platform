from fastapi import FastAPI
from pydantic import BaseModel
from backend.agents.graph import run
from backend.memory.episodic import EpisodicMemory
from backend.models.schemas import RecommendationOutput
import os, uuid

app = FastAPI(title="Meridian")
mem = EpisodicMemory()

class AnalyzeRequest(BaseModel):
    account_id: str
    interaction_text: str

class FeedbackRequest(BaseModel):
    request_id: str
    account_id: str
    risk_score: float
    risk_level: str
    recommendation_title: str
    decision: str
    modification_notes: str = ""

@app.post("/analyze", response_model=RecommendationOutput)
def analyze(req: AnalyzeRequest):
    return run(req.interaction_text, req.account_id)

@app.post("/feedback")
def feedback(req: FeedbackRequest):
    mem.log_feedback({
        "account": req.account_id,
        "risk_score": req.risk_score,
        "risk_level": req.risk_level,
        "recommendation_title": req.recommendation_title,
        "decision": req.decision,
        "modification_notes": req.modification_notes,
        "outcome": "pending",
        "timestamp": __import__("datetime").datetime.utcnow().isoformat()
    })
    return {"status": "logged"}

@app.get("/health")
def health():
    return {"status": "ok"}
