import os
import json
import importlib.util
from typing import List, Dict, Tuple

# Detect optional dependencies without importing to avoid F401
FAISS_AVAILABLE = importlib.util.find_spec("faiss") is not None or importlib.util.find_spec("faiss_cpu") is not None
CHROMA_AVAILABLE = importlib.util.find_spec("chromadb") is not None


class SimpleEmbedder:
    """
    Minimal embedder stub; replace with a proper embedding model in production.
    Uses a naive hashing-based vectorization for scaffold purposes.
    """
    dim = 128

    def encode(self, text: str):
        v = [0.0] * self.dim
        for i, ch in enumerate(text):
            v[i % self.dim] += (ord(ch) % 31) / 100.0
        return v


class RAGIndex:
    """
    RAG index with optional FAISS/Chroma backing. Falls back to in-memory linear search.
    Documents are loaded from MEDICAL_DOCS_DIR; supports .txt and .jsonl files.
    """
    def __init__(self, base_dir: str):
        self.embedder = SimpleEmbedder()
        self.base_dir = base_dir
        self.docs: List[Dict] = []
        self.vectors: List[List[float]] = []
        self._load_documents()

    def _load_documents(self):
        doc_dir = os.getenv("MEDICAL_DOCS_DIR", os.path.join(os.getcwd(), "assets", "medical_docs"))
        os.makedirs(doc_dir, exist_ok=True)
        # Load .txt files
        for name in os.listdir(doc_dir):
            path = os.path.join(doc_dir, name)
            if os.path.isdir(path):
                continue
            if name.endswith(".txt"):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        content = f.read()
                    self._add_doc({"id": name, "text": content, "source": path})
                except Exception:
                    continue
            elif name.endswith(".jsonl"):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        for line in f:
                            line = line.strip()
                            if not line:
                                continue
                            obj = json.loads(line)
                            text = obj.get("text") or obj.get("content") or ""
                            did = obj.get("id") or name
                            self._add_doc({"id": did, "text": text, "source": path})
                except Exception:
                    continue

    def _add_doc(self, doc: Dict):
        self.docs.append(doc)
        self.vectors.append(self.embedder.encode(doc["text"]))

    def _score(self, vq, vd) -> float:
        # Cosine similarity approximation
        import math
        dot = sum(a * b for a, b in zip(vq, vd))
        nq = math.sqrt(sum(a * a for a in vq)) + 1e-9
        nd = math.sqrt(sum(a * a for a in vd)) + 1e-9
        return dot / (nq * nd)

    # PUBLIC_INTERFACE
    def query(self, question: str, top_k: int = 4) -> List[Dict]:
        """
        Query the RAG store and return top_k results with scores and metadata.
        """
        vq = self.embedder.encode(question)
        scored = []
        for i, vd in enumerate(self.vectors):
            s = self._score(vq, vd)
            scored.append((s, self.docs[i]))
        scored.sort(key=lambda x: x[0], reverse=True)
        results = []
        for s, doc in scored[:top_k]:
            results.append({"id": doc["id"], "text": doc["text"], "source": doc["source"], "score": float(s)})
        return results


# PUBLIC_INTERFACE
def compose_recommendation(question: str, hits: List[Dict]) -> Tuple[str, List[Dict]]:
    """
    Compose a recommendation answer from top-k hits with simple synthesis.
    Returns (answer, citations).
    """
    if not hits:
        return (
            "No relevant guidance found in the local knowledge base. Please consult up-to-date clinical guidelines.",
            [],
        )
    summary_parts = []
    citations = []
    for i, h in enumerate(hits, start=1):
        snippet = h["text"][:300].replace("\n", " ")
        summary_parts.append(f"[{i}] {snippet}...")
        citations.append({"rank": i, "id": h["id"], "source": h["source"], "score": h["score"]})
    answer = (
        f"Based on retrieved guidance, here is a synthesized recommendation:\n"
        f"- Key points: {' '.join(summary_parts)}\n"
        f"- Please verify with current clinical protocols."
    )
    return answer, citations
