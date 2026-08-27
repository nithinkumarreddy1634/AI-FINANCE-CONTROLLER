"""
Finance Policy RAG Retriever
Retrieves policy chunks from VectorStore and constructs verifiable policy citations.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from knowledge.vector_store import VectorStore

@dataclass
class PolicyCitation:
    doc_name: str
    section: str
    content: str
    relevance_score: float
    citation_label: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "doc_name": self.doc_name,
            "section": self.section,
            "content": self.content,
            "relevance_score": self.relevance_score,
            "citation_label": self.citation_label
        }

class PolicyRetriever:
    def __init__(self, vector_store: Optional[VectorStore] = None):
        self.vector_store = vector_store or VectorStore()

    def retrieve_policy(self, query: str, top_k: int = 2) -> List[PolicyCitation]:
        raw_results = self.vector_store.similarity_search(query, top_k=top_k)
        citations = []
        for r in raw_results:
            doc_title = r["doc_name"].replace("_", " ").title()
            label = f"{doc_title}, {r['section']}"
            citations.append(PolicyCitation(
                doc_name=r["doc_name"],
                section=r["section"],
                content=r["content"],
                relevance_score=r["score"],
                citation_label=label
            ))
        return citations

