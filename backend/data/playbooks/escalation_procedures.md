# Escalation Procedures

## Overview
Escalation is not a failure — it is a structured process to mobilize the right resources when a customer situation exceeds normal CSM capacity. Speed and transparency are the two most critical factors in successful escalations.

## Severity Levels

### P0 — Critical (Response: Same day, max 4 hours)
**Definition:** Production system down, data loss, or explicit churn threat from executive.
**Examples:**
- SSO completely broken, all users locked out
- Data corruption or loss reported
- Executive sends churn notice
- Regulatory/compliance violation triggered

**Escalation path:**
1. CSM → VP Customer Success (immediate Slack DM + call)
2. VP CS → CTO/Head of Engineering if technical
3. Dedicated response team assembled within 2 hours
4. Customer gets VP-level call within 4 hours
5. Status updates every 2 hours until resolved

### P1 — High (Response: Within 24 hours)
**Definition:** Major feature broken, significant adoption regression, competitor evaluation confirmed.
**Examples:**
- Critical integration failing (Salesforce sync, SSO)
- Health score drops below 45
- DAU drops >40% in one week
- Active competitor evaluation with deadline

**Escalation path:**
1. CSM → CSM Manager (within 2 hours of identification)
2. CSM Manager reviews and assigns dedicated support resource
3. Engineering ticket filed as P1 with SLA
4. Customer response within 24 hours from CSM + Manager

### P2 — Medium (Response: Within 3 business days)
**Definition:** Recurring support issues, adoption plateau, approaching churn risk.
**Examples:**
- 5+ open tickets with no resolution progress
- Health score 45–55 for >2 consecutive weeks
- Renewal <90 days with no renewal conversation started
- NPS drop >15 points

**Escalation path:**
1. CSM flags to CSM Manager in weekly sync
2. Account tagged for enhanced monitoring
3. Structured intervention plan created within 3 days

## Escalation Communication Templates

### Internal Escalation Slack Message (P0)
```
🚨 P0 ESCALATION: [Account Name]
ARR: $XXX | Renewal: [Date]
Issue: [One sentence]
Customer Contact: [Name, Title]
Status so far: [What has been tried]
Immediate need: [What you need from leadership]
```

### Customer Acknowledgment Email (P1/P0)
```
Subject: Your Account — Immediate Action Underway

[Name],

I want you to know that I have personally escalated your situation to our leadership team. 
[Specific person name and title] is now engaged and will reach out to you within [X hours/today].

I am treating this as our highest priority. You will receive an update from me by [specific time].

[Your name]
```

## Escalation Pitfalls
- Waiting 48+ hours to escalate a P0 signal (speed is everything)
- Escalating without all context documented (wastes leadership time)
- Not closing the loop with the customer after escalation is resolved
- Over-escalating low-severity issues (trains leadership to deprioritize)
