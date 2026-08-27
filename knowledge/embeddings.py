"""
Lightweight Vector Embeddings & Similarity Engine
Provides zero-dependency vector embeddings and cosine similarity scoring.
"""

import math
import re
from typing import List, Dict, Set

class LocalVectorEmbedding:
    @staticmethod
    def tokenize(text: str) -> List[str]:
        cleaned = re.sub(r"[^\w\s]", " ", text.lower())
        return [w for w in cleaned.split() if len(w) > 2]

    @staticmethod
    def get_vector(tokens: List[str], vocabulary: List[str]) -> List[float]:
        freq = {}
        for t in tokens:
            freq[t] = freq.get(t, 0) + 1
        
        vec = []
        for term in vocabulary:
            tf = freq.get(term, 0)
            vec.append(float(tf))
        return vec

    @staticmethod
    def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        dot = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))
        if norm1 == 0.0 or norm2 == 0.0:
            return 0.0
        return round(dot / (norm1 * norm2), 4)

