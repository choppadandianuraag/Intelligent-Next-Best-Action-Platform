#!/usr/bin/env python3
"""
Seed episodic memory with pre-resolved cases from data/resolved_cases/*.json.
Run from the project root: python scripts/seed_memory.py
Confirms: memory_log count >= 6
"""
import json
import glob
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.memory.episodic import EpisodicMemory


def main():
    mem = EpisodicMemory()

    # Determine risk level from situation context
    def infer_risk_level(case: dict) -> str:
        signals = case.get("risk_signals", [])
        if len(signals) >= 4:
            return "critical"
        elif len(signals) >= 3:
            return "high"
        elif len(signals) >= 2:
            return "medium"
        return "low"

    paths = glob.glob("backend/data/resolved_cases/*.json")
    print(f"Found {len(paths)} resolved cases")

    for path in paths:
        with open(path, encoding="utf-8") as f:
            case = json.load(f)

        risk_level = infer_risk_level(case)
        mem.log_feedback(
            {
                "account": case["account_name"],
                "risk_score": 0.75 if risk_level in ("high", "critical") else 0.55,
                "risk_level": risk_level,
                "recommendation_title": case["action_taken"],
                "decision": "accept",
                "modification_notes": case["csm_notes"],
                "outcome": case["outcome"],
                "timestamp": datetime.utcnow().isoformat(),
            }
        )
        print(f"  Seeded: {case['account_name']} ({case['case_id']})")

    count = mem.conn.execute("SELECT count(*) FROM memory_log").fetchone()[0]
    print(f"\nSeeded {count} resolved cases into episodic memory.")
    assert count >= 6, f"Expected >= 6 cases, got {count}"
    print("✓ Memory seeding complete.")


if __name__ == "__main__":
    main()
