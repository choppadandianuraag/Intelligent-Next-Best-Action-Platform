# Product Guide: Automation Module

## Overview
The Automation Module lets customers create rule-based and event-driven workflows that eliminate manual tasks, reduce human error, and accelerate response times. Accounts with 10+ active automation workflows have a 31% higher renewal rate than accounts with fewer than 3.

## Core Concepts

### Triggers
An event that starts a workflow:
- **Schedule-based:** Daily at 9am, weekly on Mondays, monthly on the 1st
- **Threshold-based:** When a metric exceeds or falls below a defined value
- **Event-based:** When a new record is created, when a ticket is opened, when a user logs in for the first time

### Actions
What the workflow does:
- Send an email or Slack message
- Create a ticket in Jira/Zendesk
- Update a CRM record
- Run a report and deliver it
- Trigger a webhook to an external system
- Tag a record in the platform

### Conditions
Filters that refine when the action fires:
- Only if: DAU < 10, or ticket priority = P1, or user role = admin
- Conditions can be stacked with AND/OR logic

## Building Your First Workflow (15 minutes)

### Recommended First Workflow: Daily Alert Digest
This workflow sends a daily summary of all triggered alerts to the team lead.

1. Platform → Automation → New Workflow
2. Trigger: Schedule — Daily at 8:00 AM [customer's timezone]
3. Condition: Alerts triggered in last 24 hours > 0
4. Action: Send email → Recipients: [team lead email] → Template: "Daily Alert Digest"
5. Save and enable
6. Test: click "Run Now" and verify email is received

### High-Value Workflow Templates
- **Weekly Ops Report:** Schedule trigger → Send report → Team distribution list
- **Anomaly Escalation:** Threshold trigger (metric drops >20%) → Create Jira ticket + Slack notification to manager
- **New User Welcome:** Event trigger (first login) → Send welcome email with quick-start guide
- **Ticket Aging Alert:** Schedule trigger (daily) → Condition (ticket open >7 days) → Slack notification to CSM
- **Health Score Drop Alert:** Threshold trigger → Notify account manager

## Common Issues

### Workflow Not Triggering
- Check that the workflow is enabled (toggle in workflow list)
- Verify trigger conditions are met (use "Test Trigger" button)
- Check timezone settings — workflow schedule uses UTC by default unless timezone is explicitly set

### Emails Not Delivered
- Verify recipient list format: `name@company.com, name2@company.com` (comma-separated, no spaces)
- Check spam filter for `automation@platform.io`
- Test with a personal email address to isolate the issue

### Webhook Failing
- Verify webhook URL accepts POST requests
- Check that authentication header is correctly formatted
- Use the "Webhook Test" feature to see the exact payload being sent

## Advanced Features
- **Branching logic:** Add if/then branches within a workflow
- **Multi-step workflows:** Chain up to 10 actions in sequence
- **Rate limiting:** Set maximum workflow runs per hour to prevent alert fatigue
- **Audit log:** Every automation run is logged with timestamp, trigger data, and outcome
