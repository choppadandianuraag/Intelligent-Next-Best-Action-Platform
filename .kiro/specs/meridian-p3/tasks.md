# Meridian P3 — Frontend / Demo Lead Tasks

## Tasks

- [x] 1. Project scaffolding & mock stubs
  - Create project directory structure
  - Create requirements.txt with all dependencies
  - Create .env.example
  - Create .gitignore
  - Create mock stubs for graph.run() and EpisodicMemory so P3 runs standalone
  - **Acceptance:** Directory structure matches spec; `python -c "from backend.agents.graph import run"` works with mock

- [x] 2. Pydantic schemas (backend/models/schemas.py)
  - Implement all exact Pydantic models: AgentStep, Evidence, Action, MemoryContext, RecommendationOutput
  - **Acceptance:** `python -c "from backend.models.schemas import RecommendationOutput"` imports cleanly

- [x] 3. FastAPI backend (backend/main.py)
  - Implement POST /analyze endpoint calling graph.run()
  - Implement POST /feedback endpoint calling mem.log_feedback()
  - Implement GET /health endpoint
  - **Acceptance:** `uvicorn backend.main:app --port 8000` starts; /health returns {"status":"ok"}

- [x] 4. Frontend agent trace component (frontend/components/agent_trace.py)
  - Implement render_agent_trace(steps) with st.expander
  - Show agent name, action, reasoning, duration_ms right-aligned
  - **Acceptance:** Component renders without errors when called with sample data

- [x] 5. Frontend recommendation panel (frontend/components/recommendation_panel.py)
  - Implement render_recommendation_panel(result) with risk score, evidence cards, primary recommendation, alternatives
  - Source-type badges with color coding
  - **Acceptance:** Component renders without errors when called with sample data

- [x] 6. Frontend memory panel (frontend/components/memory_panel.py)
  - Implement render_memory_panel(ctx) — only renders when similar_cases_found > 0
  - Show similar case count, precedent accounts, confidence boost
  - **Acceptance:** Component renders correctly; skips render when similar_cases_found == 0

- [x] 7. Frontend HITL widget (frontend/components/hitl_widget.py)
  - Implement render_hitl_widget(result, account_id) with Accept / Reject / Modify buttons
  - Modify flow: text_area → submit → POST /feedback → re-run /analyze → st.rerun()
  - **Acceptance:** All three buttons call /feedback correctly

- [x] 8. Streamlit app entry point (frontend/app.py)
  - Wire sidebar: account dropdown from customer_profiles JSON, transcript textarea, Analyse button
  - On submit: call /analyze, store in session_state, render all 4 components in order
  - **Acceptance:** `streamlit run frontend/app.py` opens in browser; full flow works end-to-end

- [x] 9. Sample customer profiles (backend/data/customer_profiles/)
  - Create 5 JSON files: acme_corp.json, bluewave_tech.json, nexus_systems.json, globex_corp.json, techcorp.json
  - **Acceptance:** app.py sidebar populates with 5 account names

- [x] 10. Architecture docs (docs/ARCHITECTURE.md)
  - Write Mermaid diagram: Streamlit → FastAPI → LangGraph (5 agents) → ChromaDB → SQLite → Claude
  - **Acceptance:** Mermaid block renders on GitHub

- [x] 11. README.md
  - One-line description, prerequisites, setup commands, screenshot placeholder, team members
  - **Acceptance:** README renders correctly on GitHub

- [x] 12. Demo script (docs/demo_script.md)
  - 3-scenario arc: Acme Corp (cold start) → Globex Corp (healthy) → TechCorp (memory boost)
  - **Acceptance:** Script covers all 3 scenarios with narration cues
