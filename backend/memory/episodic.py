"""
MOCK implementation of episodic.py for standalone P3 development.
Replace with real SQLite implementation from P2 when merging.
"""
import os
from backend.models.schemas import MemoryContext

DB_PATH = os.getenv("EPISODIC_DB_PATH", "./episodic_memory.db")


class EpisodicMemory:
    def __init__(self):
        self._log = []

    def log_feedback(self, data: dict):
        self._log.append(data)
        print(f"[MOCK EpisodicMemory] Logged feedback: {data.get('decision')} for {data.get('account')}")

    def find_similar(self, risk_level: str, risk_score: float, top_n: int = 3) -> list:
        return []

    def get_memory_context(self, risk_level: str, risk_score: float) -> MemoryContext:
        return MemoryContext(
            similar_cases_found=0,
            confidence_boost=0.0,
            base_confidence=0.73,
            boosted_confidence=0.73,
            precedent_accounts=[],
        )
