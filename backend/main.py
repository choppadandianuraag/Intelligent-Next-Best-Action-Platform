"""
FastAPI backend for Meridian.

Endpoints:
  POST /analyze   — accepts AnalyzeRequest, runs agent graph, returns RecommendationOutput
  POST /feedback  — accepts FeedbackRequest, logs to episodic memory
  GET  /health    — returns {"status": "ok"}
"""
import json
import os
import re
import uuid
from contextlib import asynccontextmanager
from datetime import datetime
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
    modification_notes: str | None = None


PROFILES_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "backend", "data", "customer_profiles",
)


class CreateAccountRequest(BaseModel):
    account_name: str
    industry: str
    region: str = ""
    contract_end: str = ""
    csm: str = ""
    arr: int = 0
    primary_contact: str = ""
    primary_contact_title: str = ""
    notes: str = ""


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


@app.get("/accounts")
async def list_accounts():
    """Return all customer profiles (summary info for the dropdown)."""
    accounts = []
    if not os.path.isdir(PROFILES_DIR):
        return {"accounts": []}
    for fname in sorted(os.listdir(PROFILES_DIR)):
        if not fname.endswith(".json"):
            continue
        path = os.path.join(PROFILES_DIR, fname)
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            continue
        account_id = fname.replace(".json", "")
        accounts.append({
            "id": account_id,
            "name": data.get("account_name", account_id),
            "arr_inr": data.get("arr_inr_display", ""),
            "industry": data.get("industry", ""),
            "region": data.get("region", ""),
            "csm": data.get("csm", ""),
            "contract_end": data.get("contract_end", ""),
            "risk_level": data.get("risk_level", ""),
            "risk_score": data.get("risk_score", 0),
        })
    return {"accounts": accounts}


@app.post("/accounts")
async def create_account(request: CreateAccountRequest):
    """Create a new customer profile and return its account_id."""
    if not request.account_name.strip():
        raise HTTPException(status_code=400, detail="account_name is required")

    account_id = request.account_name.lower().replace(" ", "_").replace("-", "_")
    # Ensure uniqueness
    fpath = os.path.join(PROFILES_DIR, f"{account_id}.json")
    if os.path.exists(fpath):
        # Append a suffix
        suffix = 1
        while os.path.exists(os.path.join(PROFILES_DIR, f"{account_id}_{suffix}.json")):
            suffix += 1
        account_id = f"{account_id}_{suffix}"
        fpath = os.path.join(PROFILES_DIR, f"{account_id}.json")

    profile = {
        "account_name": request.account_name,
        "arr": request.arr,
        "arr_inr_display": f"₹{request.arr:,}" if request.arr else "",
        "industry": request.industry,
        "region": request.region,
        "contract_end": request.contract_end,
        "csm": request.csm,
        "health_score_history": [50],
        "daily_active_users": 0,
        "total_licensed_users": 0,
        "last_login_date": datetime.utcnow().strftime("%Y-%m-%d"),
        "features_adopted": [],
        "open_tickets": 0,
        "nps_score": 50,
        "risk_score": 0.5,
        "risk_level": "medium",
        "primary_contact": request.primary_contact,
        "primary_contact_title": request.primary_contact_title,
        "notes": request.notes,
    }
    with open(fpath, "w", encoding="utf-8") as f:
        json.dump(profile, f, indent=2, ensure_ascii=False)

    return {
        "status": "created",
        "account_id": account_id,
        "account": profile,
    }


def _clean_transcript(text: str) -> str:
    """Strip markdown formatting from transcript text before analysis."""
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)  # bold
    text = re.sub(r'\*(.+?)\*', r'\1', text)        # italic
    text = re.sub(r'^#{1,4}\s+', '', text, flags=re.MULTILINE)  # headings
    text = re.sub(r'\|(.+?)\|', r'\1', text)        # table pipes (keep content)
    return text.strip()


@app.post("/analyze", response_model=RecommendationOutput)
async def analyze(request: AnalyzeRequest):
    """Run the full agent pipeline for the given account and interaction text."""
    cleaned = _clean_transcript(request.interaction_text)
    if not cleaned:
        raise HTTPException(status_code=400, detail="interaction_text cannot be empty")
    if not request.account_id.strip():
        raise HTTPException(status_code=400, detail="account_id cannot be empty")

    try:
        result = run(cleaned, request.account_id)
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


@app.get("/memory")
async def get_memory_log():
    """Return the full episodic memory log (past CSM decisions)."""
    import sqlite3

    if _episodic is None:
        raise HTTPException(status_code=503, detail="Episodic memory not initialized")

    rows = _episodic.conn.execute(
        "SELECT id, account, risk_score, risk_level, recommendation_title, "
        "decision, modification_notes, outcome, timestamp "
        "FROM memory_log ORDER BY id DESC LIMIT 50"
    ).fetchall()
    cols = ["id", "account", "risk_score", "risk_level", "recommendation_title",
            "decision", "modification_notes", "outcome", "timestamp"]
    return {"entries": [dict(zip(cols, r)) for r in rows]}
