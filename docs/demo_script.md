# Meridian — 5-Minute Demo Script

**Total time:** ~5 minutes  
**Setup required:** Both servers running (`uvicorn` on :8000, `streamlit` on :8501)

---

## Before You Start

- Have the browser open at http://localhost:8501
- Have the three transcripts below ready to paste
- Run `python scripts/seed_memory.py` first so memory is pre-loaded with the 6 resolved cases

---

## Scene 1 — Acme Corp (cold start, no memory)

**Time:** 0:00 – 1:45

### Actions
1. Open Streamlit at http://localhost:8501
2. In the sidebar, select **"Acme Corp"** from the Account dropdown
3. Paste the following transcript into the text area:

```
Sarah Chen (CSM): Thanks for joining today. I wanted to check in on how things are going with the platform.

Mark Williams (VP Operations, Acme Corp): Honestly, Sarah, we're pretty frustrated. We've been paying $85,000 a year and I can barely get my team to log in. The reporting module doesn't do what we need and my CFO is asking hard questions about renewal.

Sarah: I understand. Can you tell me more about what's missing in reporting?

Mark: We need to compare performance across business units side by side. The current tool just shows everything flat. And support has taken over 2 weeks to respond to our last two tickets.

Sarah: We do have a comparison view — I wonder if it's not configured correctly for your setup. Let me look into that.

Mark: Look, our renewal is in 47 days. If we can't see a real improvement in the next few weeks, I'm going to have to recommend we evaluate alternatives. I've already had a preliminary conversation with a competitor.
```

4. Click **Analyse account**
5. Wait for the spinner to complete (~2–3 seconds with mock, ~8–12 seconds with real agents)

### What to narrate
> "Sarah just got off a difficult call. She opens Meridian and pastes the transcript. Watch what happens."

### What to point out
- **Agent trace** (expanded): 5 agents ran in sequence — planner → analyzer → retriever → assessor → generator
- **Risk score: 84%** — critical level, 4 signals detected
- **Evidence**: The system pulled from the meeting note, the churn prevention playbook, and the EBR guide
- **Primary recommendation**: "Schedule EBR within 48h" with 73% confidence
- **No memory panel** — this is a cold start, no similar cases yet

6. Click **Accept**
7. Say: "Sarah accepts the recommendation. It's now logged to memory."

---

## Scene 2 — Globex Corp (healthy, expansion)

**Time:** 1:45 – 3:00

### Actions
1. In the sidebar, select **"Globex Corp"**
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

### What to narrate
> "Now let's look at a healthy account. Same system, completely different story."

### What to point out
- **Risk score: 12%** — low, only 2 signals (both positive)
- **Primary recommendation**: "Propose enterprise upgrade this week" with 88% confidence
- **No memory panel** — this is an expansion case, memory is calibrated for at-risk scenarios
- "Meridian doesn't just detect churn — it recognises expansion opportunities and gives the CSM a concrete action with high confidence."

---

## Scene 3 — TechCorp (memory boost — this is the money moment)

**Time:** 3:00 – 5:00

### Actions
1. In the sidebar, select **"TechCorp"**
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

### What to narrate
> "TechCorp has similar risk signals to Acme Corp — struggling setup, low adoption, early churn threat. But watch what's different this time."

### What to point out
- **Memory Boost panel appears** — "2 similar cases found: Acme Corp, GlobexQ1"
- **Base confidence: 73%** → **Boosted confidence: 89%** (delta: +16%)
- "The platform remembered what worked with Acme Corp. It resolved in 14 days after an EBR. So for TechCorp, it's recommending the same approach — with higher confidence."
- Point to the `precedent_accounts` on the primary recommendation card
- **This is the differentiator**: "Every accepted recommendation makes the next recommendation smarter. This is the memory loop."

4. Click **Modify**
5. Type: "Change approach to focus on onboarding support first, EBR in 2 weeks if not resolved"
6. Click **Submit modification**
7. Say: "Sarah wants to adjust the recommendation. She submits her feedback, and Meridian re-analyses with the CSM's input factored in."
8. Show the updated result in session state

---

## Wrap-Up (optional, if time allows)

- Switch to `docs/ARCHITECTURE.md` in the browser or a code editor
- Walk through the Mermaid diagram: Streamlit → FastAPI → LangGraph → ChromaDB → SQLite → Claude
- Say: "Three people, three days, a full decision intelligence platform."

---

## Transcript Cheat Sheet

| Account | Expected Risk | Expected Primary Action |
|---------|--------------|------------------------|
| Acme Corp | 84% — Critical | Schedule EBR within 48h |
| Globex Corp | 12% — Low | Propose enterprise upgrade |
| TechCorp | 52% — Medium | Accelerate onboarding with dedicated support |
