# Health Score Methodology

## Overview
The health score is a single 0–100 composite metric representing an account's likelihood to renew and expand. It is updated daily and visible to the CSM in the platform dashboard. Understanding how it's calculated is essential for prioritizing your book of business.

## Health Score Formula

```
Health Score = (Adoption × 0.35) + (Engagement × 0.25) + (Support × 0.20) + (Sentiment × 0.20)
```

### Component: Adoption (weight 35%)
Measures feature utilization breadth and depth.
- DAU / Licensed Seats × 100 (normalized to 0–100)
- Number of features adopted / total available features × 100
- Average: above two sub-scores

**Thresholds:**
- >70%: Healthy
- 50–70%: Neutral
- <50%: At Risk

### Component: Engagement (weight 25%)
Measures recency and frequency of platform interaction.
- Days since last login by top 3 users (inverted scale)
- Session frequency trend (week-over-week change)
- Automation workflows active (0 = 0 points, 10+ = 100 points)

**Thresholds:**
- No key user login >10 days: immediate -20 point penalty
- Login daily: full score

### Component: Support (weight 20%)
Measures support ticket health and resolution velocity.
- Number of open tickets (0 = 100 points; 10+ = 0 points)
- Average ticket age (0 days = 100 points; 30+ days = 0 points)
- P0/P1 tickets: any open P0 → score capped at 40

**Thresholds:**
- 0–2 tickets, resolved <7 days: Healthy
- 5+ tickets or any ticket >14 days: At Risk

### Component: Sentiment (weight 20%)
Measures customer-reported satisfaction.
- NPS score (0–10 scale mapped to 0–100)
- Last CSM call outcome (positive/neutral/negative: 100/70/30)
- Executive sponsor engagement (active/inactive: 100/50)

**Thresholds:**
- NPS <30: Immediate health score flag
- No exec sponsor engagement >60 days: -15 points

## Health Score Thresholds and CSM Actions

| Score | Level | Description | Required CSM Action |
|-------|-------|-------------|---------------------|
| 75–100 | Green | Healthy | Standard cadence, look for expansion |
| 55–74 | Yellow | Neutral | Proactive outreach, identify gaps |
| 35–54 | Orange | At Risk | Structured intervention, EBR consideration |
| 0–34 | Red | Critical | Immediate escalation, P0 treatment |

## Score Change Triggers
The following events cause immediate recalculation:
- New support ticket opened
- Login gap >7 days detected
- NPS survey response received
- Automation workflow activated/deactivated
- CSM call logged with outcome

## Interpreting Trends
A declining trend is more important than an absolute score. An account at 62 and dropping 5 points/week is higher priority than an account at 48 that has been stable for 3 weeks.

Always look at the 5-week trend, not just today's score.
