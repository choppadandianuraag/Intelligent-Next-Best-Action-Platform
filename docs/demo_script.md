# Demo Script — Meridian 5-Minute Video

## Setup (Before Recording)
```bash
# Terminal 1
cd meridian
uvicorn backend.main:app --reload --port 8000

# Terminal 2
streamlit run frontend/app.py
```
Confirm backend health indicator shows green in sidebar.

---

## Scenario 1 — Cold Start: Acme Corp (At-Risk)

**Narrator:** "Sarah just got off a difficult call with Acme Corp's VP of Operations. Let's see what Meridian tells her to do."

**Actions:**
1. Select **"Acme Corp — At Risk"** from the account dropdown
2. Paste the contents of `backend/data/meeting_notes/acme_corp.md` into the textarea
3. Click **Analyse Account**

**Wait for results (~15-20 seconds)**

**Narrator (pointing at screen):**
- "Risk score: 84%. **Critical** level. 4 signals detected."
- "Primary recommendation: Schedule Executive Business Review within 48 hours."
- "Confidence: 73% — note there's **no memory context** yet. This is a cold start."
- "The agent trace on the right shows every step the system took: Planner → Interaction Analyzer → Knowledge Retriever → Risk Assessor → NBA Generator."

**Action:** Click **✅ Accept**

**Narrator:** "Sarah accepts the recommendation. That decision is now logged to Meridian's episodic memory."

---

## Scenario 2 — Contrast: Globex Corp (Healthy)

**Narrator:** "Now let's show that Meridian handles positive scenarios too, not just churn."

**Actions:**
1. Select **"Globex Corp — Healthy"** from the dropdown
2. Paste `backend/data/meeting_notes/globex_corp.md`
3. Click **Analyse Account**

**Narrator (pointing at screen):**
- "Risk score: 12%. **Low** risk."
- "Primary recommendation: Propose enterprise upgrade this week."
- "Confidence: 88%. The system correctly identifies an expansion opportunity, not a save play."
- "Different account, completely different playbook. Meridian adapts."

---

## Scenario 3 — The Money Moment: TechCorp + Memory

**Narrator:** "Now here's what makes Meridian different. TechCorp has similar churn signals to Acme Corp. Watch what happens."

**Actions:**
1. Select **"TechCorp — Onboarding"** from the dropdown
2. Paste `backend/data/meeting_notes/techcorp.md`
3. Click **Analyse Account**

**Narrator (pointing at screen):**
- "Risk score elevated — medium-to-high signals."
- Look at the **Memory Context panel**: *"2 similar cases found: Acme Corp, GlobexQ1"*
- "The system found 2 resolved cases with similar patterns."
- "**Confidence boosted: 73% → 89%**"
- "The NBA Generator knew these exact interventions worked before."

**Narrator (closing):**
"Sarah isn't guessing anymore. She has the collective intelligence of every case her team has resolved — surfaced automatically, in real time, with a confidence score she can act on. That's Meridian."

---

## Timing Guide
- Scenario 1: ~90 seconds
- Scenario 2: ~60 seconds
- Scenario 3: ~90 seconds
- Intro/outro: ~60 seconds
- **Total: ~5 minutes**
