#!/usr/bin/env python3
"""
Ingest all playbooks and meeting notes into the ChromaDB "knowledge_base" collection.
Run from the project root: python scripts/ingest.py
Confirm: collection.count() >= 80
"""
import os
import glob
import sys

# Allow running from project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.memory.vector_store import VectorStore


CHROMA_DIR = os.getenv("CHROMA_PERSIST_DIR", "backend/data/chroma_db")


def chunk_text(text: str, max_tokens: int = 500) -> list[str]:
    """Split text into chunks of approximately max_tokens words."""
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks = []
    for p in paragraphs:
        if len(p.split()) > max_tokens:
            sentences = p.split(". ")
            current = ""
            for s in sentences:
                if len((current + s).split()) > max_tokens:
                    if current:
                        chunks.append(current.strip())
                    current = s
                else:
                    current += (". " + s) if current else s
            if current:
                chunks.append(current.strip())
        else:
            chunks.append(p)
    return [c for c in chunks if len(c.split()) >= 5]  # drop tiny fragments


def main():
    store = VectorStore(persist_dir=CHROMA_DIR)

    total_added = 0

    # Ingest playbooks
    playbook_paths = glob.glob("backend/data/playbooks/*.md")
    print(f"Found {len(playbook_paths)} playbooks")
    for path in playbook_paths:
        with open(path, encoding="utf-8") as f:
            text = f.read()
        chunks = chunk_text(text)
        metadatas = [
            {
                "source_file": os.path.basename(path),
                "chunk_index": i,
                "category": "playbook",
            }
            for i in range(len(chunks))
        ]
        store.add(chunks, metadatas, "knowledge_base")
        total_added += len(chunks)
        print(f"  {os.path.basename(path)}: {len(chunks)} chunks")

    # Ingest meeting notes
    note_paths = glob.glob("backend/data/meeting_notes/*.md")
    print(f"Found {len(note_paths)} meeting notes")
    for path in note_paths:
        with open(path, encoding="utf-8") as f:
            text = f.read()
        chunks = chunk_text(text)
        metadatas = [
            {
                "source_file": os.path.basename(path),
                "chunk_index": i,
                "category": "meeting_note",
            }
            for i in range(len(chunks))
        ]
        store.add(chunks, metadatas, "knowledge_base")
        total_added += len(chunks)
        print(f"  {os.path.basename(path)}: {len(chunks)} chunks")

    count = store._get_or_create("knowledge_base").count()
    print(f"\nknowledge_base count: {count}")
    assert count >= 80, f"Expected >= 80 chunks, got {count}"
    print("✓ Ingestion complete and count verified.")


if __name__ == "__main__":
    main()
