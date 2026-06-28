# Meridian

**Decision intelligence for customer success teams.**

Meridian analyzes customer meeting transcripts and CRM data through a 5-agent LangGraph pipeline to generate ranked next-best-action recommendations with confidence scores that improve as the system learns from resolved cases.

---

## Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Set environment variables
```bash
cp .env.example .env
# Edit .env and set GROQ_API_KEY=your_key_here
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
cd figma/dist && python3 -m http.server 5173
# Opens at http://localhost:5173
# Or for development: cd figma && pnpm dev
```

---

## Demo Scenarios

| Scenario | Account | Expected | Key Point |
|----------|---------|----------|-----------|
| 1 — Cold start | BYJU's Learning | High/Critical risk | Budget crisis, pricing ask, memory cold start |
| 2 — Contrast | Zomato Ops | Low risk | Growth signals, expansion recommendation |
| 3 — Memory | Wipro CloudOps | High risk | Champion departure, boosted confidence by memory |

---

## Usage

1. Select an account from the sidebar dropdown
2. Paste a meeting transcript into the text area
3. Click **Analyse account**
4. Review the agent trace, risk assessment, evidence, and primary recommendation
5. Click **Accept**, **Reject**, or **Modify** to log your decision to memory

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/analyze` | Run the agent pipeline on a transcript |
| `POST` | `/feedback` | Log a CSM decision to episodic memory |
| `GET` | `/health` | Health check |

API docs available at http://localhost:8000/docs

### `POST /analyze`
```json
Request:  { "account_id": "byju_learning", "interaction_text": "..." }
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

## Project Structure

```
meridian/
├── backend/
│   ├── main.py                    # FastAPI: /analyze, /feedback, /health
│   ├── agents/
│   │   ├── graph.py               # LangGraph StateGraph + run() entrypoint
│   │   ├── planner.py             # Agent 1: schedule execution plan
│   │   ├── interaction_analyzer.py # Agent 2: extract signals via Groq/llama
│   │   ├── knowledge_retriever.py # Agent 3: ChromaDB semantic search
│   │   ├── risk_assessor.py       # Agent 4: rule-based risk scoring 0-100%
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
├── figma/
│   ├── src/
│   │   └── app/App.tsx            # React SPA entry point
│   ├── dist/                      # Pre-built static bundle
│   ├── package.json               # pnpm dependencies
│   └── vite.config.ts             # Vite build config
├── scripts/
│   ├── ingest.py                  # Embed all data/ docs into ChromaDB
│   └── seed_memory.py             # Pre-load resolved_cases into episodic memory
├── tests/
│   └── eval_scenarios.py          # 3-case eval with expected outputs
└── docs/
    ├── ARCHITECTURE.md
    └── demo_script.md
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
| `GROQ_API_KEY` | — | Required. Your Groq API key |
| `GROQ_MODEL` | `llama-3.3-70b-versatile` | Groq model to use |
| `CHROMA_PERSIST_DIR` | `backend/data/chroma_db` | ChromaDB persistence path |
| `EPISODIC_DB_PATH` | `./episodic_memory.db` | SQLite database path |
| `BACKEND_URL` | `http://localhost:8000` | Used by React frontend |

---

## Team

| Person | Role | Responsibilities |
|--------|------|-----------------|
| P1 | AI / Agents Lead | Pydantic schemas, LangGraph graph, 5 agents, prompt tuning |
| P2 | Data / Memory Lead | Sample data, ChromaDB ingestion, SQLite episodic memory |
| P3 | Frontend / Demo Lead | FastAPI server, React UI, architecture docs, demo |

---

## Architecture

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the full system diagram and agent pipeline documentation.

---

## Tech Stack

- **LangGraph** — multi-agent state machine
- **Groq llama-3.3-70b-versatile** — LLM for signal extraction, risk assessment, and NBA generation
- **ChromaDB** — vector store for knowledge base retrieval
- **SQLite** — episodic memory for CSM decision history
- **FastAPI** — REST API server
- **React + Vite** — interactive frontend (figma/)
- **Pydantic v2** — data validation and schema contracts
- **sentence-transformers** — local text embeddings (all-MiniLM-L6-v2)
