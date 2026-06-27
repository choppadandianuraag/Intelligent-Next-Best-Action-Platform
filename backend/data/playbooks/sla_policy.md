# SLA Policy

## Overview
This document defines service level agreements (SLAs) for customer support, covering response times, resolution targets, and escalation paths by severity level.

## Support Tiers

### Standard Support (Included in all plans)
- Email support during business hours (9am–6pm customer's timezone, Mon–Fri)
- Initial response SLA: 1 business day
- In-app help center and documentation access
- Monthly group office hours webinar

### Priority Support (Growth and Enterprise tiers)
- Email + Slack channel support
- Initial response SLA: 4 business hours
- Dedicated CSM with monthly health reviews
- Access to escalation hotline during business hours

### Enterprise Support (Enterprise tier only)
- 24/7 emergency support via phone for P0 incidents
- Initial response SLA: 1 business hour
- Named support engineer
- Quarterly security and compliance reviews
- Custom SLA agreements available

## Ticket Severity Definitions

### P0 — Critical
**Definition:** Production system completely unavailable, data loss, or security breach.
**Response SLA:** 1 hour (Enterprise), 4 hours (Priority), best effort (Standard)
**Resolution target:** 4 hours for system restoration; full resolution 24 hours
**Escalation:** Immediate CTO/VP Engineering notification

### P1 — High
**Definition:** Major feature broken, significant data unavailability, or severe performance degradation affecting >50% of users.
**Response SLA:** 4 hours (Priority/Enterprise), 1 business day (Standard)
**Resolution target:** 24 hours
**Escalation:** Engineering lead notified within 2 hours of ticket creation

### P2 — Medium
**Definition:** Feature degradation, non-critical integration failure, or issue affecting <50% of users with workaround available.
**Response SLA:** 1 business day (all tiers)
**Resolution target:** 5 business days

### P3 — Low
**Definition:** Minor UI issues, feature requests, documentation feedback, or questions.
**Response SLA:** 2 business days
**Resolution target:** Next product release cycle or 30 days

## SLA Measurement
SLAs are measured from the moment a ticket is submitted (automated timestamp). Response = first substantive reply from support team. Resolution = ticket closed with customer confirmation.

## Credits for SLA Breach
If a P0 SLA is breached and the customer is on Priority or Enterprise support:
- 1 day service credit for every hour beyond response SLA
- Maximum credit: 10% of monthly contract value per incident
- Credits applied to next invoice; cannot be converted to cash

## Escalation Path
1. Support ticket submitted → Auto-assigned to support queue
2. Support agent response (per SLA)
3. If unresolved at 50% of resolution target: auto-escalate to senior support
4. If unresolved at resolution target: escalate to Engineering + CSM
5. If P0 > 4 hours unresolved: Executive escalation
