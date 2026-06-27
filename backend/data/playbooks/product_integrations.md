# Product Guide: Integrations

## Overview
Integrations are the most powerful stickiness driver in the platform. Every new integration a customer activates increases their switching cost and embeds the platform deeper in their daily workflows. CSMs should proactively identify integration opportunities and facilitate setup.

## Available Integrations

### CRM Integrations
- **Salesforce** (native, bidirectional): Sync accounts, contacts, health scores, opportunity data
- **HubSpot** (native, bidirectional): Sync deals, contacts, customer health to deal view
- **Pipedrive** (native, read): Pull deal and contact data into platform dashboards

### Data Warehouse
- **Snowflake** (beta, write): Push platform metrics and processed data to Snowflake
- **BigQuery** (GA, write): Export data to Google BigQuery for custom analytics
- **Redshift** (GA, write): Export to Amazon Redshift

### Ticketing Systems
- **Jira** (native, bidirectional): Sync tickets, status, and priority
- **Jira Service Management** (native, read/write with field mapping): Requires manual field configuration for custom fields
- **Zendesk** (native, bidirectional): Full ticket sync with priority and CSAT data
- **ServiceNow** (partner, read): Read incident and request data

### Communication
- **Slack** (native): Alert notifications, report delivery, digest summaries
- **Microsoft Teams** (native): Alert notifications and weekly digests

### Identity / SSO
- **Okta** (native): SAML 2.0 SSO
- **Azure Active Directory** (native, with conditional access support in v2.1+): SAML 2.0 SSO
- **Google Workspace** (native): OAuth SSO

## Setup by Integration Type

### Salesforce Setup (15 minutes)
1. Platform → Integrations → Salesforce → Connect
2. Authenticate with Salesforce admin credentials
3. Select sync objects: Accounts, Contacts, Opportunities (recommended)
4. Set sync frequency: real-time or hourly
5. Map custom fields if needed
6. Test sync: create a test record in Salesforce, verify it appears in platform within 5 minutes

### HubSpot Setup (10 minutes)
1. Platform → Integrations → HubSpot → Connect
2. Authenticate with HubSpot admin credentials
3. Enable "Health Score in Deal View" toggle
4. Configure which pipeline stages trigger health score updates
5. Test: open a deal in HubSpot, verify health score widget appears

### Snowflake Setup (Beta — requires solutions engineer)
1. Request Snowflake beta access from your CSM
2. Provide: Snowflake account URL, warehouse name, database name
3. Solutions engineer configures connector and data schema
4. Data begins flowing within 24 hours of configuration
5. Initial historical sync: up to 72 hours

## Field Mapping for Jira Service Management
JSM custom fields do not auto-map. Required steps:
1. Integrations → Jira Service Management → Field Mapping
2. For each custom field: select the JSM field name and map to the platform destination field
3. Fields not present in the mapping interface: submit a support ticket — engineering can add them within 5 business days
4. Re-sync after mapping: Integrations → JSM → Force Sync

## Integration Health Monitoring
All integration statuses are visible at: Platform → Integrations → Status Dashboard
- Green: Syncing normally
- Yellow: Sync delayed >1 hour
- Red: Sync error — requires action

Set up an alert for integration errors: Alerts → New Alert → Integration Error → Notify [admin email]
