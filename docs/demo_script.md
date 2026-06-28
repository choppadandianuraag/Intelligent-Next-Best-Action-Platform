# Demo Script — Meridian 5-Minute Video

## Setup (Before Recording)

```bash
# Terminal 1 — Start the FastAPI backend
uvicorn backend.main:app --reload --port 8000

# Terminal 2 — Start the React frontend
cd figma/dist && python3 -m http.server 5173
```

- Run `python scripts/seed_memory.py` first so memory is pre-loaded with resolved cases
- Have the browser open at http://localhost:5173
- Confirm backend health indicator shows green in sidebar

---

## Scenario 1 — Cold Start: BYJU's Learning Operations (Critical Risk)

**Total time:** 0:00 – 1:45

**Narrator:** "Neha just got off a difficult call with BYJU's VP of Operations. Renewal is in 22 days, and there's a company-wide 30% SaaS reduction mandate. Let's see what Meridian tells her."

### Actions
1. Select **"BYJU's Learning Operations"** from the account dropdown
2. Paste the following transcript:

```
Neha Sharma (CSM): Good morning Sanjay ji. I know your renewal is coming up very soon. I wanted to have a candid conversation.

Sanjay Patel (VP Operations, BYJU's): Neha, I'll be frank. Our company has been going through a very difficult period as you know. There are budget pressures at every level. I have been asked to cut non-essential SaaS spend by 30%.

Neha: I understand the external pressures. I want to help you make a strong case internally. Can you tell me what value the team has gotten from the platform this year?

Sanjay: Honestly the operations team does find it useful — the course delivery tracking and tutor scheduling has been helpful. But I cannot quantify the exact ROI to put in front of my CFO.

Neha: I can help with that. I have prepared a usage report — your team logged 1,847 sessions this quarter, the scheduling module reduced manual coordination by an estimated 18 hours per week, and escalation resolution time dropped by 40%. Can I share that with you to present internally?

Sanjay: Yes, please send that. That might help. But Neha, I need to ask — is there any flexibility on pricing? Even a 15-20% reduction would make this conversation much easier.

Neha: I cannot commit to pricing changes myself, but I will escalate to my VP today. Given your situation and the renewal timeline, I want to bring you something by tomorrow morning.

Sanjay: That would be very appreciated. If you can get me something reasonable by tomorrow, I will fight for this renewal internally.
```

3. Click **Analyse account**
4. Wait for results (~10–15 seconds with real agents)

### What to point out
- **Agent trace** (right column, expanded): 5 agents ran in sequence — Planner → Interaction Analyzer → Knowledge Retriever → Risk Assessor → NBA Generator
- **Risk score: high/critical.** Multiple signals detected — budget pressure, ROI quantification request, pricing flexibility ask
- **Evidence**: The system pulled from the India churn prevention playbook and the Reliance Jio resolved case
- **Primary recommendation** displays with base confidence and concrete action
- **No memory context** — this is a cold start, no similar cases yet logged via HITL

### Action
Click **✅ Accept**

**Narrator:** "Neha accepts the recommendation. That decision is now logged to Meridian's episodic memory."

---

## Scenario 2 — Contrast: Zomato Operations Intelligence (Healthy — Expansion)

**Total time:** 1:45 – 3:00

**Narrator:** "Now let's show that Meridian handles positive scenarios too — not just churn."

### Actions
1. Select **"Zomato Operations Intelligence"** from the dropdown
2. Paste the following transcript:

```
Divya Reddy (CSM): Hi Abhinav! Good to connect. How's the platform working for the ops team?

Abhinav Joshi (Head of Ops Intelligence, Zomato): Divya, things are going well overall. The real-time dashboards are being used daily — our city leads love the visibility. NPS internally for the tool is solid.

Divya: That's great to hear! Are there any areas where you feel we could do more?

Abhinav: Yes, actually. We are growing very fast — we just expanded to 12 new cities in the last quarter. The platform handles our current city count fine, but I am worried about scale. When we hit 80+ cities, will the performance hold?

Divya: That is a great question to raise early. Our platform is architected to scale to several hundred data sources — we have clients with much higher volumes. But I will have our Solutions team run a capacity review specifically for your growth trajectory and give you a written assessment.

Abhinav: That would be very reassuring to have in writing. Also — we need the mobile app to be better. Our delivery partners and city managers are always on the move. The current mobile experience is clunky.

Divya: Noted. Mobile UX is something we have a major update coming for in Q3. I can get you early access to the beta if you are interested.

Abhinav: Yes, absolutely. Put us on the beta list. If the mobile experience improves, I think we are looking at a multi-year renewal conversation.

Divya: I'll make sure of that. I'll connect you with our product team for the beta access by next week.
```

3. Click **Analyse account**

### What to point out
- **Risk score: Low.** Positive signals dominate — NPS satisfaction, growth intent, multi-year renewal signal
- **Primary recommendation** focuses on expansion/multi-year renewal with high confidence
- **Evidence panel** shows the India expansion playbook and relevant resolved cases
- "Meridian doesn't just detect churn — it recognizes expansion opportunities and gives the CSM a concrete action with high confidence."

---

## Scenario 3 — The Money Moment: Wipro CloudOps + Memory Boost

**Total time:** 3:00 – 5:00

**Narrator:** "Now here's what makes Meridian different. Wipro CloudOps has a champion departure situation — we've seen other accounts with this exact pattern. Watch what happens when the system has memory."

### Actions
1. Select **"Wipro CloudOps"** from the dropdown
2. Paste the following transcript:

```
Sneha Iyer (CSM): Good afternoon Vikram ji. How has the quarter been going?

Vikram Sharma (Director of Cloud Operations, Wipro): Sneha, honestly it has been mixed. The platform is good, but we have a people problem — our champion Ananya left the company last month. She was the one who drove adoption across all three teams. Now I am not sure who owns this internally.

Sneha: Oh, I did not know about Ananya's departure. That is a significant change. Have you identified someone to take over?

Vikram: We have someone in mind — Rohan Bapat from the integration team. He has seen the platform but never been formally trained. And with Q2 closing next month, nobody has bandwidth to do a proper handover.

Sneha: I completely understand. This is actually a situation we have handled before. We have an accelerated re-onboarding program specifically for champion transitions. I can have Rohan trained and certified in 2 weeks without interrupting his Q2 work.

Vikram: That sounds promising. What does that involve?

Sneha: Three focused 90-minute sessions, self-paced modules, and I will set up office hours for his team for the first month. We have done this for two other large accounts this year and both renewed.

Vikram: If you can make that happen before end of July, I think we will be in a good place for renewal. The platform itself is solving the right problems — it is just the knowledge transfer that is the gap.

Sneha: Consider it done. I will send you a proposed schedule by end of day tomorrow.
```

3. Click **Analyse account**

### What to point out
- **Memory Boost panel appears** — similar cases found from episodic memory (e.g., Nykaa Champion Change, Reliance Jio EBR)
- **Base confidence vs Boosted confidence** — the system's confidence increases because of past resolved cases with matching risk profiles
- **`precedent_accounts`** shown on the primary recommendation card — the system tells you *which* past cases influenced this recommendation
- **"This is the differentiator: Every accepted recommendation makes the next recommendation smarter. This is the memory loop."**

### Action (optional — shows Modify flow)
1. Click **✏️ Modify**
2. Type: "Add product deep-dive session before the re-onboarding begins"
3. Click **Confirm Modification**
4. Say: "Sneha adjusts the recommendation. Her feedback is logged to episodic memory for future learning."

### Narrator (closing)
"Sneha isn't guessing anymore. She has the collective intelligence of every case her team has resolved — surfaced automatically, in real time, with a confidence score she can act on. That's Meridian."

---

## Timing Guide
- Setup/intro: ~30 seconds
- Scenario 1 (BYJU's — cold start): ~90 seconds
- Scenario 2 (Zomato — expansion contrast): ~60 seconds
- Scenario 3 (Wipro — memory boost): ~90 seconds
- Wrap-up: ~30 seconds
- **Total: ~5 minutes**

## Transcript Cheat Sheet

| Account | Expected Risk | Why |
|---------|--------------|-----|
| BYJU's Learning | High/Critical | Budget reduction mandate, pricing ask, competitor risk, 22d renewal |
| Zomato Ops | Low | Positive signals, expansion intent, multi-year renewal interest |
| Wipro CloudOps | High | Champion departure, onboarding gap, knowledge transfer risk |

## Setup Verification Checklist

- [ ] `python scripts/ingest.py` — knowledge_base count >= 80
- [ ] `python scripts/seed_memory.py` — memory_log count >= 6
- [ ] `uvicorn backend.main:app --port 8000` — server starts without errors
- [ ] `cd figma/dist && python3 -m http.server 5173` — UI opens in browser
- [ ] Account dropdown showing Indian accounts (BYJU's, Zomato, Wipro, etc.)
- [ ] Backend health indicator shows ✅ green in sidebar
- [ ] GROQ_API_KEY is set in .env
