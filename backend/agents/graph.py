"""
MOCK implementation of graph.py for standalone P3 development.
Replace with real LangGraph implementation from P1 when merging.
"""
import uuid
import json
import os
from datetime import datetime
from backend.models.schemas import (
    RecommendationOutput, AgentStep, Evidence, Action, MemoryContext
)

# Mock account data for standalone operation
MOCK_ACCOUNTS = {
    "acme_corp": {
        "account_name": "Acme Corp",
        "csm": "Sarah Chen",
        "contract_end": "2026-08-15",
        "risk_score": 0.84,
        "risk_level": "critical",
    },
    "bluewave_tech": {
        "account_name": "BlueWave Tech",
        "csm": "James Park",
        "contract_end": "2026-09-30",
        "risk_score": 0.71,
        "risk_level": "high",
    },
    "nexus_systems": {
        "account_name": "Nexus Systems",
        "csm": "Maria Lopez",
        "contract_end": "2026-07-01",
        "risk_score": 0.65,
        "risk_level": "high",
    },
    "globex_corp": {
        "account_name": "Globex Corp",
        "csm": "David Kim",
        "contract_end": "2026-12-31",
        "risk_score": 0.12,
        "risk_level": "low",
    },
    "techcorp": {
        "account_name": "TechCorp",
        "csm": "Emily Zhang",
        "contract_end": "2026-10-15",
        "risk_score": 0.52,
        "risk_level": "medium",
    },
}


def _load_account_data(account_id: str) -> dict:
    profile_path = f"backend/data/customer_profiles/{account_id}.json"
    if os.path.exists(profile_path):
        with open(profile_path) as f:
            return json.load(f)
    return MOCK_ACCOUNTS.get(account_id, {
        "account_name": account_id.replace("_", " ").title(),
        "csm": "CSM",
        "contract_end": "2026-12-31",
        "risk_score": 0.5,
        "risk_level": "medium",
    })


def run(raw_input: str, account_id: str) -> RecommendationOutput:
    """
    Mock implementation of the LangGraph pipeline.
    Returns a realistic RecommendationOutput for UI development.
    """
    account = _load_account_data(account_id)
    account_name = account.get("account_name", account_id)
    csm_name = account.get("csm", "CSM")
    renewal_date = account.get("contract_end", "2026-12-31")
    risk_score = account.get("risk_score", 0.5)
    risk_level = account.get("risk_level", "medium")

    agent_trace = [
        AgentStep(
            agent_name="planner",
            action="created_execution_plan",
            reasoning="Standard 4-agent pipeline for customer success analysis",
            duration_ms=12,
        ),
        AgentStep(
            agent_name="interaction_analyzer",
            action="extracted_signals",
            reasoning=f"Detected {3 if risk_level in ('critical','high') else 1} risk signals and {1 if risk_level in ('critical','high') else 3} positive signals from transcript",
            duration_ms=843,
        ),
        AgentStep(
            agent_name="knowledge_retriever",
            action="retrieved_knowledge",
            reasoning="Found 5 unique chunks from knowledge base matching signal context",
            duration_ms=210,
        ),
        AgentStep(
            agent_name="risk_assessor",
            action="assessed_risk",
            reasoning=f"Risk level: {risk_level}, score: {risk_score:.2f}. Key factors identified from signals.",
            duration_ms=1204,
        ),
        AgentStep(
            agent_name="nba_generator",
            action="generated_recommendations",
            reasoning="Primary: Schedule EBR within 48h, confidence: 0.73" if risk_level == "critical" else "Primary: Propose enterprise upgrade, confidence: 0.88",
            duration_ms=1560,
        ),
    ]

    evidence = [
        Evidence(
            id="ev_0",
            source_type="meeting_note",
            source_name=f"{account_name} — June 2026 Call",
            excerpt="VP mentioned contract review is imminent and team satisfaction scores have dropped significantly over the past quarter.",
            relevance_score=0.94,
        ),
        Evidence(
            id="ev_1",
            source_type="playbook",
            source_name="churn_prevention.md",
            excerpt="When renewal is within 60 days and health score drops below 50, initiate an Executive Business Review immediately to re-establish value.",
            relevance_score=0.89,
        ),
        Evidence(
            id="ev_2",
            source_type="playbook",
            source_name="ebr_guide.md",
            excerpt="EBR agenda: celebrate wins, address blockers, align on 12-month success plan, secure renewal commitment from economic buyer.",
            relevance_score=0.82,
        ),
        Evidence(
            id="ev_3",
            source_type="crm",
            source_name="CRM — Account Health",
            excerpt=f"Health score trend: declining for 5 consecutive months. Open tickets: 7. Last login: 2026-06-20.",
            relevance_score=0.77,
        ),
    ]

    memory_context = None
    if account_id == "techcorp":
        memory_context = MemoryContext(
            similar_cases_found=2,
            confidence_boost=0.16,
            base_confidence=0.73,
            boosted_confidence=0.89,
            precedent_accounts=["Acme Corp", "GlobexQ1"],
        )

    if risk_level == "critical":
        primary = Action(
            title="Schedule EBR within 48h",
            description="Arrange an Executive Business Review with the VP and your own executive sponsor within 48 hours. Bring ROI data, adoption metrics, and a tailored 90-day success plan. The goal is to re-establish strategic value before the renewal conversation escalates further.",
            confidence=0.89 if memory_context else 0.73,
            estimated_impact="High — prevents churn, secures renewal",
            evidence_ids=["ev_0", "ev_1", "ev_2"],
            precedent_accounts=memory_context.precedent_accounts if memory_context else [],
        )
        alternatives = [
            Action(
                title="Deploy reporting module adoption campaign",
                description="Run a targeted 2-week adoption campaign for the reporting module with dedicated CSM office hours, custom templates, and executive-level training.",
                confidence=0.58,
                estimated_impact="Medium — addresses root cause of dissatisfaction",
                evidence_ids=["ev_1", "ev_3"],
                precedent_accounts=[],
            ),
            Action(
                title="Escalate to VP of Customer Success",
                description="Escalate internally to bring VP-level attention. Jointly draft a risk mitigation plan with a 30-day milestone tracker.",
                confidence=0.45,
                estimated_impact="Medium — signals urgency, adds executive coverage",
                evidence_ids=["ev_0"],
                precedent_accounts=[],
            ),
        ]
    elif risk_level == "low":
        primary = Action(
            title="Propose enterprise upgrade this week",
            description="Present the enterprise tier to the account champion this week while engagement is high. Highlight API access, advanced analytics, and dedicated CSM support that aligns with their stated expansion goals.",
            confidence=0.88,
            estimated_impact="High — 15–25% ARR expansion opportunity",
            evidence_ids=["ev_0", "ev_1"],
            precedent_accounts=[],
        )
        alternatives = [
            Action(
                title="Introduce API integration workshop",
                description="Schedule a technical workshop with their engineering team to demonstrate API capabilities and design a custom integration plan.",
                confidence=0.72,
                estimated_impact="Medium — deepens product stickiness",
                evidence_ids=["ev_2"],
                precedent_accounts=[],
            ),
            Action(
                title="Co-author a case study",
                description="Partner with the account to publish a success story highlighting their ROI. Strengthens the relationship and creates social proof.",
                confidence=0.61,
                estimated_impact="Low-Medium — relationship investment",
                evidence_ids=["ev_3"],
                precedent_accounts=[],
            ),
        ]
    else:
        primary = Action(
            title="Accelerate onboarding with dedicated support",
            description="Assign a dedicated onboarding specialist for the next 30 days. Schedule weekly check-ins and provide custom training materials aligned with their use case.",
            confidence=0.89 if memory_context else 0.73,
            estimated_impact="High — prevents early churn, builds habit",
            evidence_ids=["ev_0", "ev_1"],
            precedent_accounts=memory_context.precedent_accounts if memory_context else [],
        )
        alternatives = [
            Action(
                title="Run product adoption health check",
                description="Conduct a 90-minute product audit session to identify setup blockers and map their workflow to product features.",
                confidence=0.62,
                estimated_impact="Medium — unblocks adoption",
                evidence_ids=["ev_2", "ev_3"],
                precedent_accounts=[],
            ),
            Action(
                title="Invite to customer community & webinar",
                description="Enroll the account in the next onboarding webinar series and introduce them to the customer community for peer support.",
                confidence=0.48,
                estimated_impact="Low-Medium — builds engagement",
                evidence_ids=["ev_1"],
                precedent_accounts=[],
            ),
        ]

    return RecommendationOutput(
        request_id=uuid.uuid4().hex[:12],
        account_name=account_name,
        csm_name=csm_name,
        renewal_date=renewal_date,
        risk_score=risk_score,
        risk_level=risk_level,
        signal_count=4 if risk_level in ("critical", "high") else 2,
        agent_trace=agent_trace,
        evidence=evidence,
        primary_recommendation=primary,
        alternatives=alternatives,
        memory_context=memory_context,
        generated_at=datetime.utcnow(),
    )
