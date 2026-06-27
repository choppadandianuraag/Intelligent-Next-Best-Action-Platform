"""
ChromaDB vector store wrapper.
Uses SentenceTransformer directly for embeddings (cosine space).
Collections: "knowledge_base", "resolved_cases"
"""
import chromadb
from sentence_transformers import SentenceTransformer


class VectorStore:
    def __init__(self, persist_dir: str = "backend/data/chroma_db"):
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self._get_or_create("knowledge_base")
        self._get_or_create("resolved_cases")

    def _get_or_create(self, name: str):
        try:
            return self.client.get_collection(name)
        except Exception:
            return self.client.create_collection(
                name, metadata={"hnsw:space": "cosine"}
            )

    def add(self, texts: list[str], metadatas: list[dict], collection: str):
        coll = self._get_or_create(collection)
        embeddings = self.model.encode(texts).tolist()
        existing = coll.count()
        ids = [f"{collection}_{existing + i}" for i in range(len(texts))]
        coll.add(ids=ids, documents=texts, metadatas=metadatas, embeddings=embeddings)

    def search(self, query: str, collection: str, n: int = 5) -> list[dict]:
        coll = self._get_or_create(collection)
        if coll.count() == 0:
            return []
        embedding = self.model.encode([query]).tolist()
        n_results = min(n, coll.count())
        results = coll.query(query_embeddings=embedding, n_results=n_results)
        output = []
        for i in range(len(results["ids"][0])):
            output.append(
                {
                    "id": results["ids"][0][i],
                    "excerpt": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i],
                }
            )
        return output
