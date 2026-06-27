"""
FastAPI backend for Meridian.

Endpoints:
  POST /analyze   — accepts AnalyzeRequest, runs agent graph, returns RecommendationOutput
  POST /feedback  — accepts FeedbackRequest, logs to episodic memory
  GET  /health    — returns {"status": "ok"}
"""
import os
from contextlib import asynccontextmanager
from pydantic import BaseModel

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from backend.agents.graph import run
from backend.memory.episodic import EpisodicMemory
from backend.models.schemas import RecommendationOutput

load_dotenv()


class AnalyzeRequest(BaseModel):
    account_id: str
    interaction_text: str


class FeedbackRequest(BaseModel):
    request_id: str
    decision: str
    modification_notes: str | None = ""


# In-memory cache of recent results (request_id → output dict) for feedback linking
_result_cache: dict = {}
_episodic: EpisodicMemory | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _episodic
    _episodic = EpisodicMemory()
    yield


app = FastAPI(
    title="Meridian API",
    description="Decision intelligence for customer success teams",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/analyze", response_model=RecommendationOutput)
async def analyze(request: AnalyzeRequest):
    """Run the full agent pipeline for the given account and interaction text."""
    if not request.interaction_text.strip():
        raise HTTPException(status_code=400, detail="interaction_text cannot be empty")
    if not request.account_id.strip():
        raise HTTPException(status_code=400, detail="account_id cannot be empty")

    try:
        result = run(request.interaction_text, request.account_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent pipeline failed: {str(e)}")

    # Cache result for feedback linkage
    _result_cache[result.request_id] = result.model_dump(mode="json")
    if len(_result_cache) > 200:
        oldest = next(iter(_result_cache))
        del _result_cache[oldest]

    return result


@app.post("/feedback")
async def feedback(request: FeedbackRequest):
    """Log CSM decision on a recommendation to episodic memory."""
    cached = _result_cache.get(request.request_id)

    if _episodic is None:
        raise HTTPException(status_code=503, detail="Episodic memory not initialized")

    _episodic.log_feedback(
        {
            "account": cached.get("account_name", "unknown") if cached else "unknown",
            "risk_score": cached.get("risk_score") if cached else None,
            "risk_level": cached.get("risk_level") if cached else None,
            "recommendation_title": (
                cached.get("primary_recommendation", {}).get("title") if cached else None
            ),
            "decision": request.decision,
            "modification_notes": request.modification_notes,
            "outcome": None,
            "timestamp": __import__("datetime").datetime.utcnow().isoformat(),
        }
    )

    return {
        "status": "logged",
        "request_id": request.request_id,
        "decision": request.decision,
    }
