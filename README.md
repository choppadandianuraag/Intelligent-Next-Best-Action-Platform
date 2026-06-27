# Meridian

**Decision intelligence for customer success teams.**

Meridian is a multi-agent AI platform that analyses customer meeting transcripts, assesses churn risk, and recommends next-best actions — learning from past decisions to improve confidence over time.

---

## Screenshot

![Recommendation Panel](docs/screenshot.png)

---

## Prerequisites

- Python 3.11+
- `pip`
- `git`
- An [Anthropic API key](https://console.anthropic.com/)

---

## Setup

```bash
# 1. Clone the repository
git clone <repo-url>
cd meridian

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env and set: ANTHROPIC_API_KEY=your-key-here

# 4. Ingest knowledge base into ChromaDB
python scripts/ingest.py
# Expected output: "knowledge_base count: <n>" (should be >= 80)

# 5. Seed episodic memory with resolved cases
python scripts/seed_memory.py
# Expected output: "Seeded 6 resolved cases into memory."

# 6. Start the FastAPI backend
uvicorn backend.main:app --reload --port 8000

# 7. In a new terminal, start the Streamlit frontend
streamlit run frontend/app.py
```

Open http://localhost:8501 in your browser.

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

---

## Project Structure

```
meridian/
├── backend/
│   ├── main.py              # FastAPI app
│   ├── agents/              # LangGraph agents (planner, analyzer, retriever, assessor, generator)
│   ├── memory/              # ChromaDB vector store + SQLite episodic memory
│   ├── models/schemas.py    # Pydantic data models
│   └── data/                # Meeting notes, playbooks, customer profiles, resolved cases
├── frontend/
│   ├── app.py               # Streamlit entry point
│   └── components/          # Agent trace, recommendation panel, memory panel, HITL widget
├── scripts/
│   ├── ingest.py            # Embed data into ChromaDB
│   └── seed_memory.py       # Pre-load resolved cases into SQLite
├── docs/
│   ├── ARCHITECTURE.md      # System architecture with Mermaid diagram
│   └── demo_script.md       # 3-scenario demo walkthrough
└── tests/
    └── eval_scenarios.py    # End-to-end evaluation test cases
```

---

## Team

| Person | Role | Responsibilities |
|--------|------|-----------------|
| P1 | AI / Agents Lead | Pydantic schemas, LangGraph graph, 5 agents, prompt tuning |
| P2 | Data / Memory Lead | Sample data, ChromaDB ingestion, SQLite episodic memory |
| P3 | Frontend / Demo Lead | FastAPI server, Streamlit UI, architecture docs, demo |

---

## Architecture

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the full system diagram and agent pipeline documentation.

---

## Tech Stack

- **LangGraph** — multi-agent state machine
- **Anthropic Claude** — LLM for signal extraction, risk assessment, and NBA generation
- **ChromaDB** — vector store for knowledge base retrieval
- **SQLite** — episodic memory for CSM decision history
- **FastAPI** — REST API server
- **Streamlit** — interactive frontend
- **Pydantic v2** — data validation and schema contracts
- **sentence-transformers** — local text embeddings (all-MiniLM-L6-v2)
