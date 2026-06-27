# Meeting Notes — Globex Corp
**Date:** 2026-06-20
**Participants:** Alex Rivera (CSM), Karen Wu (Head of Analytics, Globex Corp), Raj Patel (Engineering Manager, Globex Corp)
**Duration:** 40 minutes
**Account:** Globex Corp | ARR: $145,000 | Contract End: 2026-12-15

---

**Alex:** Karen, Raj — great to connect. I wanted to start by saying your usage metrics this quarter have been exceptional.

**Karen:** It's been a strong quarter for us. The platform has become genuinely central to how we operate. Our analysts are in it every single day. We've onboarded the entire analytics team — 58 users now — and we're pushing the limits of what we can do.

**Alex:** That's fantastic. What are you finding you're pushing up against?

**Raj:** Honestly, the API. We want to build custom integrations — we have internal tooling we've built in-house and we want to pull data programmatically rather than through the UI. The current API rate limits are too restrictive for what we want to do, and the endpoints for bulk data export don't exist yet.

**Alex:** What does that use case look like concretely?

**Raj:** We want to pipe your data into our internal data warehouse — Snowflake — and combine it with our own product analytics. We're building dashboards in Tableau that layer your metrics alongside ours. Right now we're doing this with CSV exports, which is painful and unreliable.

**Karen:** And it's not just an engineering problem. Our VP asked in our last all-hands whether we should be on an enterprise tier. We've been on the same plan for 18 months and we've probably 3x'd our usage. When's the right time to have that conversation?

**Alex:** Karen, I think that time is now. The enterprise tier gives you full API access, including bulk export endpoints, higher rate limits — 10x what you're on now — and a dedicated Snowflake connector that's currently in beta. I can get you into that beta program.

**Raj:** That Snowflake connector is literally what we've been waiting for. How long has that been a thing?

**Alex:** It went into beta last month. We've got 3 customers in it and the feedback has been very positive. I should have flagged this for you sooner — that's on me.

**Karen:** What's the pricing difference?

**Alex:** Enterprise is a step up from your current $145K ARR. Based on your usage — 58 users, your data volume — we'd be looking at roughly $210K annually. But with the Snowflake connector and full API access, the ROI math on engineering time alone probably closes that gap quickly.

**Raj:** If we can eliminate the CSV export process, that's saving my team probably 3–4 hours a week. That's real money.

**Karen:** Alex, let's have a proper proposal conversation. Can you put together a breakdown of enterprise features and pricing for our VP? We'd want to move by end of Q3.

**Alex:** Absolutely. I'll have a formal proposal to you by end of this week. And I'd suggest we set up a technical deep-dive with Raj and our solutions engineer to scope the Snowflake integration properly.

**Raj:** That works. Let's do that before the proposal goes to the VP, so we can speak to it technically.

---

**Action items logged:**
- Alex to prepare formal enterprise upgrade proposal by end of week
- Schedule technical deep-dive: Raj + Meridian solutions engineer for Snowflake scoping
- Alex to enroll Globex in Snowflake connector beta program
- Target timeline: enterprise move by end of Q3
- NPS: 72 — account health excellent
