# Demo Script — Meridian 5-Minute Video

## Setup (Before Recording)

```bash
# Terminal 1 — Start the FastAPI backend
uvicorn backend.main:app --reload --port 8000

# Terminal 2 — Start the Streamlit frontend
streamlit run frontend/app.py
```

- Run `python scripts/seed_memory.py` first so memory is pre-loaded with the 6 resolved cases
- Have the browser open at http://localhost:8501
- Confirm backend health indicator shows green in sidebar

---

## Scenario 1 — Cold Start: Acme Corp (At-Risk)

**Total time:** 0:00 – 1:45

**Narrator:** "Sarah just got off a difficult call with Acme Corp's VP of Operations. Let's see what Meridian tells her to do."

### Actions
1. Select **"Acme Corp — At Risk"** from the account dropdown
2. Paste the following transcript:

```
Sarah Chen (CSM): Thanks for joining today. I wanted to check in on how things are going with the platform.

Mark Williams (VP Operations, Acme Corp): Honestly, Sarah, we're pretty frustrated. We've been paying $85,000 a year and I can barely get my team to log in. The reporting module doesn't do what we need and my CFO is asking hard questions about renewal.

Sarah: I understand. Can you tell me more about what's missing in reporting?

Mark: We need to compare performance across business units side by side. The current tool just shows everything flat. And support has taken over 2 weeks to respond to our last two tickets.

Sarah: We do have a comparison view — I wonder if it's not configured correctly for your setup. Let me look into that.

Mark: Look, our renewal is in 47 days. If we can't see a real improvement in the next few weeks, I'm going to have to recommend we evaluate alternatives. I've already had a preliminary conversation with a competitor.
```

3. Click **Analyse account**
4. Wait for results (~10–15 seconds with real agents)

### What to point out
- **Agent trace** (right column, expanded): 5 agents ran in sequence — Planner → Interaction Analyzer → Knowledge Retriever → Risk Assessor → NBA Generator
- **Risk score: 84%. Critical level.** 4 signals detected
- **Evidence**: The system pulled from the meeting note, the churn prevention playbook, and the EBR guide
- **Primary recommendation**: "Schedule Executive Business Review within 48h" with 73% confidence
- **No memory context** — this is a cold start, no similar cases yet

### Action
Click **✅ Accept**

**Narrator:** "Sarah accepts the recommendation. That decision is now logged to Meridian's episodic memory."

---

## Scenario 2 — Contrast: Globex Corp (Healthy)

**Total time:** 1:45 – 3:00

**Narrator:** "Now let's show that Meridian handles positive scenarios too, not just churn."

### Actions
1. Select **"Globex Corp — Healthy"** from the dropdown
2. Paste the following transcript:

```
David Kim (CSM): Great to connect, Rachel. The QBR numbers look fantastic this quarter.

Rachel Torres (Head of Operations, Globex Corp): Yes, the team loves the platform. We're at 94% adoption across all five features. Actually, I wanted to ask — we're planning to onboard 3 more business units in Q3. Is there an enterprise tier that would cover that?

David: Absolutely. The enterprise tier includes unlimited seats, dedicated API access, and a dedicated CSM pod.

Rachel: The API access is key for us — we want to build our own dashboards pulling from your data. What's the timeline to get a scoping call with your technical team?

David: I can set that up for next week. Our engineering team loves working with customers like you on custom integrations.

Rachel: Perfect. And our NPS score is apparently 68 — I hope that earns us a good rate!
```

3. Click **Analyse account**

### What to point out
- **Risk score: 12%. Low risk.** Only 2 positive signals
- **Primary recommendation**: "Propose enterprise upgrade this week" with 88% confidence
- **No memory panel** — this is an expansion case, memory is calibrated for at-risk scenarios
- "Meridian doesn't just detect churn — it recognizes expansion opportunities and gives the CSM a concrete action with high confidence."

---

## Scenario 3 — The Money Moment: TechCorp + Memory

**Total time:** 3:00 – 5:00

**Narrator:** "Now here's what makes Meridian different. TechCorp has similar churn signals to Acme Corp. Watch what happens."

### Actions
1. Select **"TechCorp — Onboarding"** from the dropdown
2. Paste the following transcript:

```
Emily Zhang (CSM): Hi Marcus, just checking in on your second week with the platform.

Marcus Lee (IT Manager, TechCorp): Emily, I appreciate the check-in. Honestly, setup has been rougher than we expected. We haven't been able to connect our CRM yet and only 3 of our 18 users have logged in this week.

Emily: That's concerning. What's blocking the CRM integration?

Marcus: Our IT team says the documentation isn't clear about the OAuth flow. We've opened a ticket but it's been 5 days without a response.

Emily: I apologize for that — that's too long. Let me escalate that internally today.

Marcus: I hope so. Our management signed off on this to improve team efficiency. If we can't get the setup done in the next two weeks, we're going to have to reconsider whether this was the right decision.
```

3. Click **Analyse account**

### What to point out
- **Memory Boost panel appears** — "2 similar cases found: Acme Corp, GlobexQ1"
- **Base confidence: 73% → Boosted confidence: 89%** (delta: +16%)
- "The platform remembered what worked with Acme Corp. It resolved in 14 days after an EBR. So for TechCorp, it's recommending the same approach — with higher confidence."
- Point to the `precedent_accounts` on the primary recommendation card
- **"This is the differentiator: Every accepted recommendation makes the next recommendation smarter. This is the memory loop."**

### Action (optional — shows Modify flow)
1. Click **✏️ Modify**
2. Type: "Change approach to focus on onboarding support first, EBR in 2 weeks if not resolved"
3. Click **Confirm Modification**
4. Say: "Sarah wants to adjust the recommendation. She submits her feedback, and Meridian logs it to episodic memory for future learning."

### Narrator (closing)
"Sarah isn't guessing anymore. She has the collective intelligence of every case her team has resolved — surfaced automatically, in real time, with a confidence score she can act on. That's Meridian."

---

## Timing Guide
- Setup/intro: ~30 seconds
- Scenario 1 (Acme Corp): ~90 seconds
- Scenario 2 (Globex Corp): ~60 seconds
- Scenario 3 (TechCorp + memory): ~90 seconds
- Wrap-up: ~30 seconds
- **Total: ~5 minutes**

## Transcript Cheat Sheet

| Account | Expected Risk | Expected Primary Action |
|---------|--------------|------------------------|
| Acme Corp | 84% — Critical | Schedule EBR within 48h |
| Globex Corp | 12% — Low | Propose enterprise upgrade |
| TechCorp | 52% — Medium | Accelerate onboarding with dedicated support |

## Setup Verification Checklist

- [ ] `python scripts/ingest.py` — knowledge_base count >= 80
- [ ] `python scripts/seed_memory.py` — memory_log count >= 6
- [ ] `uvicorn backend.main:app --port 8000` — server starts without errors
- [ ] `streamlit run frontend/app.py` — UI opens in browser
- [ ] Backend health indicator shows ✅ green in sidebar
- [ ] GROQ_API_KEY is set in .env
