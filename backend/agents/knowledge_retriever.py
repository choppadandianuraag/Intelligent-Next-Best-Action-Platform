import json
import time
from typing import List, Dict

from backend.agents.llm_client import call_llm
from backend.memory.vector_store import VectorStore
from backend.models.schemas import Evidence


def _build_enhanced_queries(signals: list) -> list[str]:
    """
    Use the LLM to rewrite raw signal text into richer search queries
    that retrieve more relevant results from the vector store.

    Falls back to programmatically enriched queries if the LLM call fails.
    """
    # Fast fallback — enrich queries without an LLM call
    def _fallback(sig: dict) -> str:
        text = sig.get("text", "")
        stype = sig.get("type", "")
        severity = sig.get("severity", "")
        context_terms = {
            ("risk", "high"): "urgent churn risk signal — ",
            ("risk", "medium"): "at-risk customer signal — ",
            ("risk", "low"): "minor customer concern — ",
            ("positive", "high"): "strong positive customer signal — ",
            ("positive", "medium"): "positive customer signal — ",
            ("positive", "low"): "slightly positive customer signal — ",
            ("neutral", ""): "neutral customer observation — ",
        }
        prefix = context_terms.get((stype, severity), context_terms.get((stype, ""), ""))
        return f"{prefix}{text}"

    if not signals:
        return []

    # Build prompt for the LLM
    signal_lines = []
    for i, s in enumerate(signals, 1):
        signal_lines.append(
            f"  Signal {i}: \"{s.get('text', '')}\" | "
            f"type={s.get('type', '')} | severity={s.get('severity', '')}"
        )
    signals_str = "\n".join(signal_lines)

    prompt = (
        "You are a search query optimizer for a B2B SaaS customer success knowledge base. "
        "Given the signals below from a meeting transcript, rewrite each signal's text "
        "into a richer, more specific search query that will retrieve the most relevant "
        "knowledge-base articles, playbooks, meeting notes, and resolved cases.\n\n"
        f"{signals_str}\n\n"
        "Return ONLY a JSON object with a single key 'queries' containing an array of "
        "rewritten queries — one per signal, in the same order.\n\n"
        "Rules:\n"
        "- Expand short phrases into full, descriptive sentences (10–30 words each)\n"
        "- Include CS domain context: 'customer success', 'churn prevention', "
        "'renewal risk', 'account escalation', 'SaaS', 'B2B'\n"
        "- Make each query specific enough to find the right evidence "
        "but general enough to match semantically similar chunks\n"
        "- Do NOT fabricate details — stay faithful to the original signal text\n\n"
        "Example:\n"
        'Input:  "budget pressure" | type=risk | severity=high\n'
        'Output: "Customer facing company-wide budget cuts and cost reduction '
        'mandate affecting SaaS renewal decisions with urgent pricing request"'
    )

    try:
        raw = call_llm(prompt, max_tokens=1024, temperature=0, json_mode=True)
        parsed = json.loads(raw)
        llm_queries = parsed.get("queries", [])
        if len(llm_queries) == len(signals) and all(llm_queries):
            return llm_queries
    except Exception:
        pass

    # Fallback: programmatic enrichment
    return [_fallback(s) for s in signals]


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
    """Convert raw search results into Evidence objects with correct source_type."""
    evidence_list = []
    for idx, r in enumerate(results):
        distance = r.get("distance", 0.5)
        relevance = max(0.0, min(1.0, 1.0 - (distance / 2.0)))

        # Determine source_type from collection tag or metadata category
        collection = r.get("_collection", "knowledge_base")
        metadata = r.get("metadata", {})
        category = metadata.get("category", "")

        if collection == "resolved_cases":
            source_type = "memory"
        elif category == "meeting_note":
            source_type = "meeting_note"
        elif category == "playbook":
            source_type = "playbook"
        else:
            source_type = "playbook"  # fallback

        evidence_list.append(
            Evidence(
                id=f"ev_{idx}",
                source_type=source_type,
                source_name=r.get("metadata", {}).get("source_file", "unknown"),
                excerpt=r.get("excerpt", ""),
                relevance_score=round(relevance, 3),
            ).model_dump()
        )
    return evidence_list


def retrieve(state: dict) -> dict:
    """
    Knowledge Retriever node: for each signal in state['signals'],
    queries BOTH the knowledge_base AND resolved_cases collections
    and returns deduplicated Evidence objects with correct source types.
    """
    start = time.time()

    store = VectorStore()
    all_results: List[Dict] = []

    signals = state.get("signals", [])

    # Step 1: Build enriched queries (LLM-rewritten if available, fallback otherwise)
    enriched_queries = _build_enhanced_queries(signals)

    if enriched_queries and len(enriched_queries) == len(signals):
        # Search with enriched queries — one per signal
        for query in enriched_queries:
            if not query.strip():
                continue
            kb_results = store.search(query=query, collection="knowledge_base", n=5)
            for r in kb_results:
                r["_collection"] = "knowledge_base"
            all_results.extend(kb_results)

            rc_results = store.search(query=query, collection="resolved_cases", n=3)
            for r in rc_results:
                r["_collection"] = "resolved_cases"
            all_results.extend(rc_results)

        # Step 2: Also generate a combined contextual query (all signals together)
        # to catch cross-signal connections the per-signal searches might miss
        combined_snippets = [q for q in enriched_queries if q.strip()]
        if combined_snippets:
            combined_query = " ".join(combined_snippets[:3])  # top 3 signals
            kb_combined = store.search(query=combined_query, collection="knowledge_base", n=3)
            for r in kb_combined:
                r["_collection"] = "knowledge_base"
            all_results.extend(kb_combined)

            rc_combined = store.search(query=combined_query, collection="resolved_cases", n=2)
            for r in rc_combined:
                r["_collection"] = "resolved_cases"
            all_results.extend(rc_combined)

    deduped = _deduplicate(all_results)
    evidence = _build_evidence(deduped)

    duration_ms = max(1, round((time.time() - start) * 1000))

    step = {
        "agent_name": "knowledge_retriever",
        "action": "retrieved_knowledge",
        "reasoning": f"Found {len(evidence)} unique chunks from knowledge_base + resolved_cases",
        "duration_ms": duration_ms,
    }
    state["agent_trace"].append(step)

    return {"knowledge_chunks": evidence, "agent_trace": state["agent_trace"]}
