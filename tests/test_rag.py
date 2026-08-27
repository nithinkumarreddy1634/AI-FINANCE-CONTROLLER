"""
Unit tests for Knowledge Base Vector Store, Ingestion, and Policy Retriever.
"""

from knowledge import VectorStore, LocalVectorEmbedding, PolicyRetriever, ingest_finance_policies

def test_vector_embeddings_and_cosine():
    v1 = LocalVectorEmbedding.get_vector(["settlement", "delay", "days"], ["delay", "days", "settlement", "window"])
    v2 = LocalVectorEmbedding.get_vector(["settlement", "window", "days"], ["delay", "days", "settlement", "window"])
    sim = LocalVectorEmbedding.cosine_similarity(v1, v2)
    assert sim > 0.5

def test_vector_store_ingestion_and_retrieval(tmp_path):
    store_file = str(tmp_path / "test_vector_store.json")
    store = VectorStore(store_path=store_file)
    store.add_chunk("settlement_policy", "Section 1", "Settlement window delay of up to 3 days is acceptable.")
    store.build_index()

    retriever = PolicyRetriever(vector_store=store)
    citations = retriever.retrieve_policy("date settlement delay window", top_k=1)
    assert len(citations) == 1
    assert "Settlement Policy" in citations[0].citation_label
    assert citations[0].relevance_score > 0.0

