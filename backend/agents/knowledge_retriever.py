import time
from typing import List, Dict

from backend.memory.vector_store import VectorStore
from backend.models.schemas import Evidence


def _deduplicate(results: List[Dict]) -> List[Dict]:
    """Deduplicate search results by source_file + first 100 chars of excerpt."""
    seen = set()
    deduped = []
    for r in results:
        source = r.get("metadata", {}).get("source_file", "")
        excerpt = r.get("excerpt", "")[:100]
        key = (source, excerpt)
        if key not in seen:
            seen.add(key)
            deduped.append(r)
    return deduped


def _build_evidence(results: List[Dict]) -> List[dict]:
    """Convert raw search results into Evidence objects with sequential IDs."""
    evidence_list = []
    for idx, r in enumerate(results):
        distance = r.get("distance", 0.5)
        relevance = max(0.0, min(1.0, 1.0 - (distance / 2.0)))
        evidence_list.append(
            Evidence(
                id=f"ev_{idx}",
                source_type="playbook",
                source_name=r.get("metadata", {}).get("source_file", "unknown"),
                excerpt=r.get("excerpt", ""),
                relevance_score=round(relevance, 3),
            ).model_dump()
        )
    return evidence_list


def retrieve(state: dict) -> dict:
    """
    Knowledge Retriever node: for each signal in state['signals'],
    queries the vector store for relevant knowledge articles and
    returns deduplicated Evidence objects.
    """
    start = time.time()

    store = VectorStore()
    all_results: List[Dict] = []

    signals = state.get("signals", [])
    for signal in signals:
        query = signal.get("text", "")
        if not query:
            continue
        results = store.search(query=query, collection="knowledge_base", n=5)
        all_results.extend(results)

    deduped = _deduplicate(all_results)
    evidence = _build_evidence(deduped)

    duration_ms = max(1, round((time.time() - start) * 1000))

    step = {
        "agent_name": "knowledge_retriever",
        "action": "retrieved_knowledge",
        "reasoning": f"Found {len(evidence)} unique chunks from knowledge base",
        "duration_ms": duration_ms,
    }
    state["agent_trace"].append(step)

    return {"knowledge_chunks": evidence, "agent_trace": state["agent_trace"]}
