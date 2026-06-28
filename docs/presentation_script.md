# Meridian — 10-Minute Presentation Script (India Data)
### XLV Hackathon | 3 Presenters | Architecture (5 min) + Demo (5 min)

---

## Speaker Roles

| Speaker | Section | Time |
|---------|---------|------|
| **Person 1** | System Introduction + Agent Architecture + Indian Data | Arch min 0–2:30 |
| **Person 2** | Memory System + Explainability + Design Decisions | Arch min 2:30–5:00 |
| **Person 3** | Demo Narration — BYJU's, Zomato, Wipro | Demo min 5:00–10:00 |

---

---

# PART 1 — ARCHITECTURE WALKTHROUGH (5 Minutes)

---

## 🎤 PERSON 1 (Minutes 0:00 – 2:30)
### "System Introduction + Agent Pipeline + Indian Data"

---

**[0:00 – 0:40] — What Meridian Is**

> "Meridian is a **multi-agent decision intelligence platform** built for customer success teams.
>
> At its core it does three things: it reads a meeting transcript, reasons over a knowledge base and historical case memory, and outputs a ranked set of next-best actions — each with a confidence score, a supporting evidence chain, and a full explainable reasoning trace.
>
> Every component is modular. The agent graph is a stateful LangGraph pipeline. The memory is two-layered — ChromaDB for semantic search, SQLite for episodic decisions. The frontend is a React app over a FastAPI backend with Pydantic-validated contracts throughout.
>
> The problem context: a B2B SaaS CSM like Neha Sharma might manage 40 accounts simultaneously. A missed signal on one account — a budget freeze, a champion departure, an unanswered ticket — can cost ₹38 lakhs in ARR. Meridian surfaces that signal and tells the CSM exactly what to do, backed by the outcomes of every case the team has previously resolved."

---

**[0:40 – 1:20] — System Architecture Overview**

> *(Switch to the architecture diagram — the LangGraph pipeline flow)*
>
> "Let me walk through the architecture.
>
> The entry point is a **FastAPI server** on port 8000. The frontend — a React SPA — sends a POST to `/analyze` with two fields: `account_id` and the raw meeting transcript.
>
> That request immediately invokes the **LangGraph StateGraph** defined in `backend/agents/graph.py`. LangGraph is Google's stateful agent orchestration framework — it compiles a directed graph of agent nodes and executes them sequentially, passing a shared TypedDict state object through the entire pipeline.
>
> The state object is the single source of truth across all agents. It carries the raw transcript, extracted signals, knowledge chunks, the risk assessment, final recommendations, and the full agent trace. No agent communicates with another directly — they all read from and write to this shared contract. Adding a new downstream agent is 3 lines of graph wiring."

---

**[1:20 – 2:00] — The 5 Agent Nodes**

> *(Walk through each node on the diagram)*
>
> **Node 1 — Planner:** Pure Python. No LLM. Reads the raw input, sets the execution plan, logs the first `AgentStep` to the trace. Deterministic and instant.
>
> **Node 2 — Interaction Analyzer:** This is where Groq's Llama 3.3 70B runs in JSON mode. It extracts typed signals from the transcript — `risk`, `positive`, or `neutral` — each tagged with a severity level. This step captures semantic nuance: "budget pressure" is medium risk; "evaluation of a named competitor with an active POC" is high risk. That distinction matters downstream.
>
> **Node 3 — Knowledge Retriever:** Runs `sentence-transformers/all-MiniLM-L6-v2` locally — no extra API key. For each extracted signal, it queries ChromaDB using cosine similarity and returns the top 5 evidence chunks from our knowledge base and resolved case collections.
>
> **Node 4 — Risk Assessor:** Pure Python formula. High-severity signals contribute 0.12 each to the risk score. Medium signals add 0.06. Positive signals reduce by 0.15. The result is a score from 0 to 1 with a mapped level — critical, high, medium, or low. Fully auditable, zero hallucination risk.
>
> **Node 5 — NBA Generator:** Rule-based logic tiered by risk level. It pulls episodic memory context from SQLite, applies the confidence boost formula, and returns one primary action plus two ranked alternatives — each with a confidence score, impact description, and linked evidence IDs."

---

**[2:00 – 2:30] — Indian Enterprise Data**

> "For this demo we built a complete Indian enterprise dataset. Eight customer profiles — BYJU's Learning Operations, Zomato Ops Intelligence, Wipro CloudOps, TCS Digital, HDFC Fintech, and Ola Electric. Six India-specific playbooks covering SaaS renewal risk, champion change, pricing negotiation, and enterprise expansion. Six resolved cases drawn from companies like Reliance Jio, Nykaa, and Swiggy.
>
> All ingested via `python scripts/ingest.py`. ChromaDB chunks at 500 tokens, embeds with the local model, builds the index automatically. 368 chunks total across both collections.
>
> Extending to a new domain is the same process: point the ingest script at any folder of markdown files. The pipeline, memory system, and UI require zero changes."

---

## 🎤 PERSON 2 (Minutes 2:30 – 5:00)
### "Memory System + Design Decisions + Platform Summary"

---

**[2:30 – 3:20] — The Two-Layer Memory System**

> *(Switch to memory architecture section of the diagram)*
>
> "Let me go deeper on the memory system — it's the part that makes this a platform rather than a stateless tool.
>
> Layer one is **semantic memory** — ChromaDB with two named collections. `knowledge_base` holds our playbook and meeting transcript chunks. `resolved_cases` holds historical case summaries. For our India dataset these are real enterprise situations: the Reliance Jio data sync crisis, the Nykaa champion departure, the Swiggy EBR renewal. Cosine similarity retrieval means the Knowledge Retriever surfaces the most contextually relevant precedents for *this specific account and this specific set of signals* — not just the most recent cases.
>
> Layer two is **episodic memory** — SQLite, table `memory_log`. Every CSM decision — Accept, Reject, or Modify — is written here with the full risk context: account, risk score, risk level, recommendation title, decision type, and timestamp.
>
> The two layers work together through the NBA Generator. Before generating recommendations, it calls `get_memory_context(risk_level, risk_score)`, which queries SQLite for the closest matching prior decisions and computes the confidence boost:
>
> `Boosted Confidence = Base Confidence × (1 + 0.06 × Similar Cases Found)`
>
> Two resolved cases found: base 73% → **82%**. Five cases: **97%**. The system's confidence grows with every decision the team logs. That is a structural compounding property — not a feature, a property of the architecture."

---

**[3:20 – 4:00] — Explainability + Technical Design Decisions**

> "Explainability was a hard architectural constraint from day one, not a UI afterthought. Here is how it is enforced at the data model level.
>
> Every response is a `RecommendationOutput` Pydantic v2 model. It includes: an `agent_trace` — a list of `AgentStep` objects, one per node, each with `agent_name`, `action`, `reasoning`, and `duration_ms`. An `evidence` list — the exact `Evidence` objects retrieved from ChromaDB, each with `source_type`, `source_name`, `excerpt`, and `relevance_score`. And a `memory_context` — the `MemoryContext` object showing `similar_cases_found`, `base_confidence`, `boosted_confidence`, and `precedent_accounts`.
>
> The UI surfaces every field. A CSM presenting a recommendation to their VP can explain the exact evidence and the exact formula behind the confidence score. No black box.
>
> On the infrastructure side: FastAPI for async, auto-documented API. Pydantic v2 throughout — the response contract is machine-verifiable. Groq for low-latency LLM calls with native JSON mode — no output parsing fragility. All secrets via environment variables, zero hardcoding."

---

**[4:00 – 5:00] — Platform Summary + Eval Fit**

> "Let me be explicit about what makes this a platform and not just a demo script.
>
> **Stateful typed graph** — the LangGraph StateGraph with a TypedDict state object means every agent has a guaranteed, versioned interface. You extend the pipeline by adding nodes; you don't rewrite anything.
>
> **Pluggable LLM** — the model is one environment variable. Today: Groq Llama 3.3 70B. Switch to GPT-4o, Claude, or a local Ollama model without touching a single agent file.
>
> **Domain-agnostic retrieval** — ChromaDB doesn't know or care what domain the content is from. The same vector store interface works for CS playbooks today and legal contracts or procurement risk tomorrow.
>
> **Persistent institutional knowledge** — the SQLite episodic memory survives restarts, deployments, and team changes. Every decision is retained. A new CSM on day one inherits the full reasoning history of the team.
>
> **Configurable risk model** — severity weights, risk thresholds, tier definitions are all named Python constants. A business analyst changes the risk model; no agent code changes.
>
> That's the system. Now let's see it run."

---

---

# PART 2 — DEMO VIDEO (5 Minutes)
## 🎤 PERSON 3 (Minutes 5:00 – 10:00)
### "3 Indian Enterprise Scenarios — Live on Screen"

> *(React SPA at http://localhost:5173, backend running, all Indian data ingested)*

---

**[5:00 – 5:20] — System Orientation**

> "What you're looking at is the Meridian dashboard — React frontend talking to FastAPI on port 8000.
>
> Left sidebar: account selector, backend health indicator, and the memory panel. Center: transcript input and results. Right column: the full live agent trace.
>
> Three scenarios. Three completely different system outputs — because the pipeline reasons from the evidence, not from templates."

---

**[5:20 – 7:00] — Scenario 1: BYJU's Learning Operations (Cold Start — Critical Risk)**

> *(Select `byju_learning` from the dropdown. Paste the BYJU's transcript. Click Analyse.)*
>
> "Scenario one — BYJU's Learning Operations, Bengaluru. ARR: ₹38 lakhs. Renewal: 22 days out.
>
> Transcript: CSM Neha Sharma on a call with VP Operations Sanjay Patel. Sanjay communicated a company-wide 30% SaaS reduction mandate. He needs a pricing answer by tomorrow. He can't demonstrate ROI to his CFO. And he mentioned he's had a preliminary conversation with a competitor.
>
> *(Wait ~15 seconds for pipeline to complete)*
>
> Risk score: **82%. Critical.** The Interaction Analyzer pulled 4 signals — budget pressure at high severity, ROI quantification request, competitive evaluation, and renewal urgency.
>
> Evidence panel: the Knowledge Retriever surfaced our India churn prevention playbook and — specifically — the Reliance Jio resolved case, where a budget-driven at-risk situation was turned around with an EBR and pricing flexibility within 14 days.
>
> Primary recommendation: **Deliver ROI business case and escalate pricing flexibility to VP within 24 hours.** Confidence: **73%.**
>
> Notice that 73%. This is a cold start — no prior decisions in episodic memory for BYJU's-type situations. The system is reporting accurate uncertainty.
>
> Agent trace on the right: Planner at 0ms, Interaction Analyzer at 2.3s, Knowledge Retriever at 0.4s, Risk Assessor at 0ms, NBA Generator at 0.1s. Complete audit trail, every step.
>
> Clicking **Accept**. That decision is now written to `memory_log` in SQLite — account, risk score, risk level, recommendation title, CSM, timestamp. Persisted."

---

**[7:00 – 7:50] — Scenario 2: Zomato Operations Intelligence (Healthy — Expansion)**

> *(Select `zomato_ops`. Paste the Zomato transcript. Click Analyse.)*
>
> "Scenario two — Zomato Operations Intelligence, Gurugram. ARR: ₹55 lakhs. 75 days to renewal.
>
> CSM Divya Reddy's call: Abhinav Joshi is a power user — city leads are running dashboards daily, NPS is 71. He's asking about expanding to 80+ cities and wants early access to the mobile update. These are positive signals at medium-to-high severity.
>
> *(Wait for results)*
>
> Risk score: **18%. Low.** The Risk Assessor's weighted formula reflects the absence of risk signals and the presence of multiple positive ones. Completely different classification path.
>
> Primary recommendation: **Propose multi-year renewal with capacity commitment and mobile beta access.** Confidence: **88%.**
>
> Same 5 nodes. Same state machine. The pipeline output is entirely driven by what the Interaction Analyzer extracted and what the Knowledge Retriever found — in this case, the expansion playbook and a resolved upsell case from the Nykaa data.
>
> This is why the evidence panel matters — you can trace exactly why the system recommended expansion and not intervention."

---

**[7:50 – 9:30] — Scenario 3: Wipro CloudOps (Memory Boost)**

> *(Select `wipro_cloudops`. Paste the Wipro transcript. Click Analyse.)*
>
> "Scenario three — this is where the memory architecture becomes visible.
>
> Wipro CloudOps, Bengaluru. ARR: ₹95 lakhs. Director Vikram Sharma to CSM Sneha Iyer: their platform champion Ananya Krishnan has left the company. The new stakeholder, Rohan Bapat, has no onboarding. Q2 is closing. Classic champion departure risk pattern.
>
> *(Wait for results)*
>
> Risk score: **68%. High.** Now look at the memory panel.
>
> **'2 similar cases found — Nykaa Champion Change, Reliance Jio EBR.'**
>
> The NBA Generator called `get_memory_context('high', 0.68)`. SQLite returned two prior decisions with matching risk level and close risk scores — both accepted. The formula runs:
>
> `0.73 × (1 + 0.06 × 2) = 0.73 × 1.12 = 0.82`
>
> Confidence without memory: **73%.** Confidence with memory: **82%.**
>
> And the recommendation itself changed — not just the score. The primary action is: **Launch accelerated champion re-onboarding program for Rohan Bapat within 10 days.** The `precedent_accounts` field on that action card shows `['Nykaa Champion Change', 'Reliance Jio EBR']` — the system surfaced *why* it chose this action, not just what the action is.
>
> We accepted the BYJU's decision in Scenario 1. That's in episodic memory. Wipro exhibits a similar risk profile. The NBA Generator connected those cases automatically, without any explicit programming of that relationship.
>
> At 100 accepted decisions — at 500 — the system is carrying the complete, searchable reasoning history of every case the team has ever resolved. A new CSM on their first week operates with the full institutional intelligence of the entire organisation."

---

**[9:30 – 10:00] — Closing**

> "Meridian is fully functional and running on Indian enterprise data right now — source code, architecture docs, and setup guide all in the GitHub repo.
>
> The architecture is domain-agnostic. The same 5-agent graph, the same two-layer memory, and the same Pydantic-validated evidence chain can be applied to procurement risk, legal review, or sales deal scoring with no changes to the orchestration layer.
>
> Confidence compounds with every accepted decision. Institutional knowledge persists and retrieves automatically.
>
> That's Meridian. Thank you."

---

---

## ⏱️ Timing Reference

| Segment | Speaker | Time |
|---------|---------|------|
| System introduction + problem context | Person 1 | 0:00 – 0:40 |
| Architecture overview + LangGraph state | Person 1 | 0:40 – 1:20 |
| The 5 agent nodes | Person 1 | 1:20 – 2:00 |
| Indian enterprise dataset | Person 1 | 2:00 – 2:30 |
| Two-layer memory system | Person 2 | 2:30 – 3:20 |
| Explainability + design decisions | Person 2 | 3:20 – 4:00 |
| Platform summary + eval fit | Person 2 | 4:00 – 5:00 |
| Demo system orientation | Person 3 | 5:00 – 5:20 |
| Scenario 1: BYJU's (Critical, cold start) | Person 3 | 5:20 – 7:00 |
| Scenario 2: Zomato (Low, expansion) | Person 3 | 7:00 – 7:50 |
| Scenario 3: Wipro (High, memory boost) | Person 3 | 7:50 – 9:30 |
| Closing | Person 3 | 9:30 – 10:00 |

---

## 🎯 Key Lines to Memorise

**Person 1:**
> *"No agent communicates with another directly — they all read from and write to a shared contract."*

**Person 2:**
> *"The system's confidence grows with every decision the team logs. That is a structural compounding property — not a feature, a property of the architecture."*

**Person 3:**
> *"The NBA Generator connected those cases automatically, without any explicit programming of that relationship."*

---

## 📋 Pre-Demo Checklist
- [ ] Indian data ingested into ChromaDB: `python scripts/ingest.py --source sample_data_india`
- [ ] Indian resolved cases seeded: `python scripts/seed_memory.py --source sample_data_india`
- [ ] Backend running: `source venv/bin/activate && GROQ_API_KEY=gsk_... python -m uvicorn backend.main:app --port 8000`
- [ ] Frontend running: `cd figma/dist && python3 -m http.server 5173`
- [ ] Browser open at http://localhost:5173, full screen
- [ ] Account dropdown showing: `byju_learning`, `zomato_ops`, `wipro_cloudops`
- [ ] BYJU's transcript ready to paste (`sample_data_india/meeting_notes/byju_learning.md`)
- [ ] Zomato transcript ready to paste (`sample_data_india/meeting_notes/zomato_ops.md`)
- [ ] Wipro transcript ready to paste (`sample_data_india/meeting_notes/wipro_cloudops.md`)
- [ ] Memory panel visible on sidebar
- [ ] Agent trace panel expanded on the right

---

## 📁 Demo Account Quick Reference

| Demo | Account | Account ID | ARR | Risk | Key Signal |
|------|---------|-----------|-----|------|-----------|
| Scenario 1 | BYJU's Learning Operations | `byju_learning` | ₹38L | 82% Critical | Budget cuts + pricing ask |
| Scenario 2 | Zomato Operations Intelligence | `zomato_ops` | ₹55L | 18% Low | Scaling + multi-year intent |
| Scenario 3 | Wipro CloudOps | `wipro_cloudops` | ₹95L | 68% High | Champion departure → memory boost |
