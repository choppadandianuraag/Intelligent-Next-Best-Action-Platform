# Meridian

**Decision intelligence for customer success teams.**

Meridian analyzes customer meeting transcripts and CRM data through a 5-agent LangGraph pipeline to generate ranked next-best-action recommendations with confidence scores that improve as the system learns from resolved cases.

---

## Quick Start

### 1. Install dependencies
```bash
cd meridian
pip install -r requirements.txt
```

### 2. Set environment variables
```bash
cp .env.example .env
# Edit .env and set ANTHROPIC_API_KEY
```

### 3. Ingest knowledge base
```bash
python scripts/ingest.py
# Expected output: knowledge_base count: >= 80
```

### 4. Seed episodic memory
```bash
python scripts/seed_memory.py
# Expected output: Seeded 6 resolved cases into episodic memory.
```

### 5. Start backend
```bash
uvicorn backend.main:app --reload --port 8000
# Verify: curl http://localhost:8000/health → {"status": "ok"}
```

### 6. Start frontend
```bash
streamlit run frontend/app.py
# Opens at http://localhost:8501
```

---

## Demo Scenarios

| Scenario | Account | Expected | Key Point |
|----------|---------|----------|-----------|
| 1 — Cold start | Acme Corp | 84% critical risk | EBR recommendation, 73% confidence, no memory |
| 2 — Contrast | Globex Corp | 12% low risk | Expansion recommendation, 88% confidence |
| 3 — Memory | TechCorp | Similar signals to Acme | Confidence boosted 73% → 89%, 2 precedent cases |

---

## Repository Structure

```
meridian/
├── backend/
│   ├── main.py                    # FastAPI: /analyze, /feedback, /health
│   ├── agents/
│   │   ├── graph.py               # LangGraph StateGraph + run() entrypoint
│   │   ├── planner.py             # Agent 1: schedule execution plan
│   │   ├── interaction_analyzer.py # Agent 2: extract signals via Claude
│   │   ├── knowledge_retriever.py # Agent 3: ChromaDB semantic search
│   │   ├── risk_assessor.py       # Agent 4: Claude risk scoring 0-100%
│   │   └── nba_generator.py       # Agent 5: generate recommendations + memory boost
│   ├── memory/
│   │   ├── vector_store.py        # ChromaDB wrapper (knowledge_base + resolved_cases)
│   │   └── episodic.py            # SQLite episodic memory (memory_log)
│   ├── models/
│   │   └── schemas.py             # Pydantic v2: all shared types
│   └── data/
│       ├── meeting_notes/         # 10 × .md transcripts
│       ├── playbooks/             # 15 × .md knowledge articles
│       ├── customer_profiles/     # 5 × .json CRM snapshots
│       └── resolved_cases/        # 6 × .json for memory seeding
├── frontend/
│   ├── app.py                     # Streamlit entry point
│   └── components/
│       ├── agent_trace.py         # Pipeline trace expander
│       ├── recommendation_panel.py # Risk gauge + action cards
│       ├── memory_panel.py        # Memory context + confidence boost viz
│       └── hitl_widget.py         # Accept / Modify / Reject buttons
├── scripts/
│   ├── ingest.py                  # Embed all data/ docs into ChromaDB
│   └── seed_memory.py             # Pre-load resolved_cases into episodic memory
├── tests/
│   └── eval_scenarios.py          # 5-case eval with expected outputs
└── docs/
    ├── ARCHITECTURE.md
    └── demo_script.md
```

---

## API Reference

### `POST /analyze`
```json
Request:  { "account_id": "acme_corp", "interaction_text": "..." }
Response: RecommendationOutput (see schemas.py)
```

### `POST /feedback`
```json
Request:  { "request_id": "...", "decision": "accepted|modified|rejected", "modification_notes": "..." }
Response: { "status": "logged", "request_id": "...", "decision": "..." }
```

### `GET /health`
```json
Response: { "status": "ok" }
```

---

## Running Tests
```bash
pytest tests/eval_scenarios.py -v
```

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ANTHROPIC_API_KEY` | — | Required. Your Anthropic API key |
| `ANTHROPIC_MODEL` | `claude-3-5-sonnet-20241022` | Claude model to use |
| `CHROMA_PERSIST_DIR` | `backend/data/chroma_db` | ChromaDB persistence path |
| `EPISODIC_DB_PATH` | `./episodic_memory.db` | SQLite database path |
| `BACKEND_URL` | `http://localhost:8000` | Used by Streamlit frontend |

---

## Team

- **P1 — AI/Agents Lead:** schemas · graph · 5 agents
- **P2 — Data/Memory Lead:** data files · vector_store · episodic · scripts
- **P3 — Frontend/Demo Lead:** FastAPI · Streamlit · components · docs
