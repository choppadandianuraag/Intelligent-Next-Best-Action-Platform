"""
SQLite-based episodic memory for Meridian.
Stores and retrieves past feedback decisions for confidence boosting.
"""

import os
import sqlite3
from backend.models.schemas import MemoryContext

DB_PATH = os.getenv("EPISODIC_DB_PATH", "./episodic_memory.db")


class EpisodicMemory:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self._init_table()

    def _init_table(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS memory_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account TEXT,
                risk_score REAL,
                risk_level TEXT,
                recommendation_title TEXT,
                decision TEXT,
                modification_notes TEXT,
                outcome TEXT,
                timestamp TEXT
            )
        """)
        self.conn.commit()

    def log_feedback(self, data: dict):
        self.conn.execute(
            """
            INSERT INTO memory_log (
                account, risk_score, risk_level, recommendation_title,
                decision, modification_notes, outcome, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data.get("account"),
                data.get("risk_score"),
                data.get("risk_level"),
                data.get("recommendation_title"),
                data.get("decision"),
                data.get("modification_notes"),
                data.get("outcome"),
                data.get("timestamp"),
            ),
        )
        self.conn.commit()

    def find_similar(
        self, risk_level: str, risk_score: float, top_n: int = 3
    ) -> list[dict]:
        cursor = self.conn.execute(
            """
            SELECT * FROM memory_log
            WHERE risk_level = ?
            ORDER BY ABS(risk_score - ?) ASC
            LIMIT ?
            """,
            (risk_level, risk_score, top_n),
        )
        cols = [d[0] for d in cursor.description]
        return [dict(zip(cols, row)) for row in cursor.fetchall()]

    def get_memory_context(
        self, risk_level: str, risk_score: float
    ) -> MemoryContext:
        cases = self.find_similar(risk_level, risk_score, top_n=3)
        similar = len(cases)
        base = 0.73
        boosted = min(base * (1 + 0.06 * similar), 0.97)
        precedent = list({c["account"] for c in cases if c.get("account")})
        return MemoryContext(
            similar_cases_found=similar,
            confidence_boost=round(boosted - base, 3),
            base_confidence=base,
            boosted_confidence=round(boosted, 3),
            precedent_accounts=precedent,
        )
