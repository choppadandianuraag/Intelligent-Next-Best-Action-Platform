# Product Guide: Reporting Module

## Overview
The Reporting Module enables customers to create automated, scheduled, and on-demand reports from their platform data. It is one of the highest-value features for driving ROI visibility and executive buy-in. Low adoption of the reporting module is strongly correlated with churn risk.

## Key Capabilities
- Custom report builder with drag-and-drop metric selection
- Scheduled delivery (daily, weekly, monthly) via email
- PDF and shareable link export
- 15+ pre-built report templates
- Custom date ranges and segment filters
- Multi-metric comparison views
- Drill-down from summary to individual records

## Setup Guide (30–45 minutes)

### Step 1: Access the Reporting Module
Navigate to: Platform → Analytics → Reports → New Report

### Step 2: Choose a Template or Start from Scratch
**Recommended for first-time users:** Start with the "Weekly Operations Summary" pre-built template. It includes the 5 most commonly requested metrics and can be customized.

### Step 3: Select Your Metrics
The report builder has four metric categories:
- **Activity Metrics:** DAU, session duration, feature usage
- **Health Metrics:** Alert triggers, automation activity, integration sync status
- **Business Metrics:** Tickets resolved, workflows completed, data processed
- **Custom Metrics:** Any field from connected data sources

Tip: Keep first reports to 5–7 metrics. Complex reports are harder to communicate internally.

### Step 4: Configure Delivery
- Recipient list: Add team members by email
- Schedule: Choose frequency (recommend weekly for operational reports, monthly for executive summaries)
- Format: PDF (for executives), shareable link (for teams)

### Step 5: Test Run
Always run a test report before scheduling. Use the "Preview" button to see exactly what recipients will see.

## Common Issues and Fixes

### Issue: Data connector not populating report fields
**Cause:** Connector sync hasn't completed or is misconfigured.
**Fix:** Go to Integrations → Check connector status. If status is "Error," re-authenticate the connector. If sync is pending, wait 15 minutes.

### Issue: Report shows "No data available" for date range
**Cause:** The selected date range predates when the connector was first configured.
**Fix:** Adjust date range to start from the connector activation date. Data before activation cannot be backfilled.

### Issue: Scheduled reports not arriving in inbox
**Cause:** Email delivery blocked by spam filter or recipient list error.
**Fix:** Add `reports@platform.io` to your organization's email whitelist. Verify recipient email addresses.

### Issue: Jira Service Management custom fields not appearing
**Cause:** JSM uses a different field schema than standard Jira. Custom fields require manual field mapping.
**Fix:** Go to Integrations → Jira Service Management → Field Mapping. Map custom fields manually. Contact support if specific fields are missing from the mapping interface.

## Adoption Tips for CSMs
- Run the first report setup live in a screen-share session — don't just send documentation
- Pre-build a template report for the customer before the setup call
- Identify the metric the executive sponsor cares most about — build the first report around that
- The "Executive Summary" pre-built template is ideal for first exec sponsor touchpoints
