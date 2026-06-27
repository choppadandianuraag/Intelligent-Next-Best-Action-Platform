# Meridian — Architecture

## System Overview

Meridian is a multi-agent decision intelligence system for customer success teams. It analyzes customer interaction transcripts and CRM data to generate ranked next-best-action recommendations, with confidence scores that improve as the system learns from resolved cases.

```
┌─────────────────────────────────────────────────────────┐
│                    Streamlit Frontend                    │
│  Sidebar: Account picker + Transcript input             │
│  Main: Risk panel · Memory panel · Agent trace · HITL   │
└────────────────────────┬────────────────────────────────┘
                         │ HTTP (httpx)
                         ▼
┌─────────────────────────────────────────────────────────┐
│                   FastAPI Backend                        │
│  POST /analyze · POST /feedback · GET /health           │
└────────────────────────┬────────────────────────────────┘
                         │ graph.run()
                         ▼
┌─────────────────────────────────────────────────────────┐
│              LangGraph StateGraph Pipeline               │
│                                                         │
│  [Planner] → [Interaction Analyzer] →                   │
│  [Knowledge Retriever] → [Risk Assessor] →              │
│  [NBA Generator]                                        │
└────────┬──────────────────────────────┬─────────────────┘
         │                              │
         ▼                              ▼
┌─────────────────┐          ┌──────────────────────────┐
│  ChromaDB       │          │  SQLite Episodic Memory   │
│  (Persistent)   │          │  (memory_log table)       │
│                 │          │                           │
│  knowledge_base │          │  Seeded from 6 resolved   │
│  resolved_cases │          │  cases + CSM decisions    │
└─────────────────┘          └──────────────────────────┘
```

## Agent Descriptions

### Planner
- **Input:** raw_input, account_id
- **Output:** execution_plan (always all 4 agents in fixed order)
- **Role:** Parses the request, logs an AgentStep with reasoning, schedules downstream agents
- **Model:** Pure Python (no LLM call)

### Interaction Analyzer
- **Input:** raw_input (transcript)
- **Output:** signals: list[{text, type, severity}]
- **Role:** Prompts Claude to extract typed signals (risk/positive/neutral) with severity levels
- **Model:** Claude 3.5 Sonnet

### Knowledge Retriever
- **Input:** signals
- **Output:** knowledge_chunks: list[Evidence], memory_context: MemoryContext
- **Role:** Semantic search over ChromaDB knowledge_base (top 5) and resolved_cases (top 3); computes confidence boost
- **Model:** sentence-transformers/all-MiniLM-L6-v2 (local)

### Risk Assessor
- **Input:** signals, knowledge_chunks, customer_profile
- **Output:** risk: {score, level, signal_count, key_signals, reasoning}
- **Role:** Prompts Claude to score churn probability 0-100% and classify (critical/high/medium/low)
- **Model:** Claude 3.5 Sonnet

### NBA Generator
- **Input:** all previous state, memory_context
- **Output:** recommendations: {primary: Action, alternatives: list[Action]}
- **Role:** Prompts Claude to generate primary + 2 alternative actions; applies memory confidence boost
- **Model:** Claude 3.5 Sonnet

## Memory Architecture

### Vector Memory (ChromaDB)
- **knowledge_base**: 80+ chunks from 15 playbooks + 10 transcripts, embedded with all-MiniLM-L6-v2
- **resolved_cases**: 6+ resolved case summaries for semantic similarity matching
- Populated by `scripts/ingest.py` and `scripts/seed_memory.py`

### Episodic Memory (SQLite)
- **memory_log table**: Every CSM decision (accept/modify/reject) logged with account, risk level, risk score, recommendation title
- `EpisodicMemory.get_memory_context()` queries by risk_level + risk_score proximity
- Confidence boost: +6% per similar case found, capped at 97%

## The Memory Demo (Confidence Boost)

The "money moment" is Scenario 3 of the demo:
1. After accepting Acme Corp recommendation (Scenario 1), that decision is in episodic memory
2. TechCorp has similar churn signals
3. Knowledge Retriever finds matching resolved cases
4. NBA Generator receives memory_context and boosts confidence from 73% → 89%
5. Memory panel shows: "2 similar cases found: Acme Corp, GlobexQ1"

## Data Flow

```
Transcript + Account ID
        │
        ▼
    Planner: schedule agents, log step
        │
        ▼
    Interaction Analyzer: extract signals via Claude
        │
        ▼
    Knowledge Retriever: ChromaDB search → Evidence + MemoryContext
        │
        ▼
    Risk Assessor: Claude scores risk 0-100%
        │
        ▼
    NBA Generator: Claude generates Action + 2 alternatives, apply memory boost
        │
        ▼
    RecommendationOutput (Pydantic) → FastAPI → Streamlit
```

## Technology Choices

| Component | Technology | Reason |
|-----------|-----------|--------|
| Agent orchestration | LangGraph | Stateful graph with typed state dict |
| LLM | Anthropic Claude 3.5 Sonnet | Best reasoning for structured JSON output |
| Vector embeddings | sentence-transformers/all-MiniLM-L6-v2 | Fast, local, no API key needed |
| Vector DB | ChromaDB (persistent) | Simple, embeds locally, cosine similarity |
| Episodic memory | SQLite | Zero config, sufficient for demo scale |
| API | FastAPI | Async, auto-docs, Pydantic integration |
| Frontend | Streamlit | Rapid demo UI, minimal setup |
