"""
Knowledge Retriever agent — semantic search over ChromaDB.
Searches knowledge_base (top 5) and resolved_cases for memory context.
Returns knowledge_chunks: list[Evidence] and memory_context: MemoryContext.
"""
import os
import time
import uuid

from backend.memory.vector_store import VectorStore
from backend.models.schemas import AgentStep, Evidence, MemoryContext

CHROMA_DIR = os.getenv("CHROMA_PERSIST_DIR", "backend/data/chroma_db")
_store = None


def _get_store() -> VectorStore:
    global _store
    if _store is None:
        _store = VectorStore(persist_dir=CHROMA_DIR)
    return _store


def knowledge_retriever_node(state: dict) -> dict:
    start = time.time()
    signals = state.get("signals", [])
    store = _get_store()

    # Build a composite query from risk signals
    risk_signals = [s for s in signals if s.get("type") == "risk"]
    all_signals = signals[:5]  # cap to avoid very long queries
    query = " ".join(s.get("text", "") for s in all_signals)
    if not query.strip():
        query = state.get("raw_input", "")[:500]

    # Search knowledge base (top 5)
    kb_results = store.search(query, "knowledge_base", n=5)
    knowledge_chunks = []
    for r in kb_results:
        meta = r.get("metadata", {})
        ev = Evidence(
            id=str(uuid.uuid4()),
            source_type="playbook" if meta.get("category") == "playbook" else "meeting_note",
            source_name=meta.get("source_file", "unknown"),
            excerpt=r.get("excerpt", "")[:400],
            relevance_score=round(max(0.0, 1.0 - r.get("distance", 1.0)), 3),
        )
        knowledge_chunks.append(ev.model_dump())

    # Search resolved cases for memory context
    rc_results = store.search(query, "resolved_cases", n=3)
    similar_count = len(rc_results)
    precedent_accounts = list(
        {r.get("metadata", {}).get("account_name", "") for r in rc_results if r.get("metadata", {}).get("account_name")}
    )

    base_confidence = 0.73
    boost = 0.06 * similar_count
    boosted = round(min(base_confidence * (1 + boost), 0.97), 3)

    memory_context = None
    if similar_count > 0:
        memory_context = MemoryContext(
            similar_cases_found=similar_count,
            confidence_boost=round(boosted - base_confidence, 3),
            base_confidence=base_confidence,
            boosted_confidence=boosted,
            precedent_accounts=precedent_accounts,
        ).model_dump()

    duration_ms = int((time.time() - start) * 1000)

    step = AgentStep(
        agent_name="Knowledge Retriever",
        action=f"Retrieved {len(knowledge_chunks)} knowledge chunks; {similar_count} similar resolved cases",
        reasoning=(
            f"Searched knowledge_base with composite signal query. "
            f"Top sources: {', '.join(set(c['source_name'] for c in knowledge_chunks[:3]))}. "
            f"Memory: {similar_count} resolved case(s) matched — "
            + (f"confidence boost +{round(boosted - base_confidence, 2):.0%}" if similar_count > 0 else "no memory boost")
        ),
        duration_ms=duration_ms,
    )

    agent_trace = state.get("agent_trace", [])
    agent_trace.append(step.model_dump())

    return {
        **state,
        "knowledge_chunks": knowledge_chunks,
        "memory_context": memory_context,
        "agent_trace": agent_trace,
    }
