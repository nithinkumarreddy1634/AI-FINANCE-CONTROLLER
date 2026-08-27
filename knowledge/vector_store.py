"""
Local Vector Store
Indexed vector database for finance policy chunk storage and similarity retrieval.
"""

import json
import os
from typing import List, Dict, Any, Optional
from knowledge.embeddings import LocalVectorEmbedding

class VectorStore:
    def __init__(self, store_path: str = os.path.join("data", "vector_store.json")):
        self.store_path = store_path
        self.chunks: List[Dict[str, Any]] = []
        self.vocabulary: List[str] = []
        self.load()

    def add_chunk(self, doc_name: str, section: str, content: str):
        tokens = LocalVectorEmbedding.tokenize(f"{doc_name} {section} {content}")
        self.chunks.append({
            "doc_name": doc_name,
            "section": section,
            "content": content,
            "tokens": tokens
        })
        # Update vocabulary
        vocab_set = set(self.vocabulary)
        vocab_set.update(tokens)
        self.vocabulary = sorted(list(vocab_set))

    def build_index(self):
        for chunk in self.chunks:
            chunk["vector"] = LocalVectorEmbedding.get_vector(chunk["tokens"], self.vocabulary)
        self.save()

    def save(self):
        os.makedirs(os.path.dirname(self.store_path), exist_ok=True)
        data = {
            "vocabulary": self.vocabulary,
            "chunks": [
                {
                    "doc_name": c["doc_name"],
                    "section": c["section"],
                    "content": c["content"],
                    "tokens": c["tokens"],
                    "vector": c.get("vector", [])
                }
                for c in self.chunks
            ]
        }
        with open(self.store_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def load(self):
        if os.path.exists(self.store_path):
            try:
                with open(self.store_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.vocabulary = data.get("vocabulary", [])
                    self.chunks = data.get("chunks", [])
            except Exception:
                self.chunks = []
                self.vocabulary = []

    def similarity_search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        if not self.chunks or not self.vocabulary:
            return []

        q_tokens = LocalVectorEmbedding.tokenize(query)
        q_vector = LocalVectorEmbedding.get_vector(q_tokens, self.vocabulary)

        scored = []
        for chunk in self.chunks:
            c_vector = chunk.get("vector")
            if not c_vector or len(c_vector) != len(q_vector):
                c_vector = LocalVectorEmbedding.get_vector(chunk["tokens"], self.vocabulary)

            sim = LocalVectorEmbedding.cosine_similarity(q_vector, c_vector)
            scored.append({
                "doc_name": chunk["doc_name"],
                "section": chunk["section"],
                "content": chunk["content"],
                "score": sim
            })

        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:top_k]

