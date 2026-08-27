"""
Knowledge Base Ingestion Pipeline
Parses finance policy documents from knowledge_base/, creates chunks, and builds the vector index.
Can be executed directly via: python -m knowledge.ingestion
"""

import os
import glob
from knowledge.vector_store import VectorStore

def ingest_finance_policies(kb_dir: str = "knowledge_base", store_path: str = os.path.join("data", "vector_store.json")):
    vector_store = VectorStore(store_path=store_path)
    vector_store.chunks = []
    vector_store.vocabulary = []

    md_files = glob.glob(os.path.join(kb_dir, "*.md"))
    if not md_files:
        print(f"No policy documents found in '{kb_dir}'. Creating default index.")
        return vector_store

    total_chunks = 0
    for file_path in md_files:
        doc_name = os.path.basename(file_path).replace(".md", "")
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        sections = content.split("## ")
        for sec in sections:
            if not sec.strip():
                continue
            lines = sec.strip().split("\n")
            section_title = lines[0].strip()
            section_body = "\n".join(lines[1:]).strip()

            if section_body:
                vector_store.add_chunk(
                    doc_name=doc_name,
                    section=section_title,
                    content=section_body
                )
                total_chunks += 1

    vector_store.build_index()
    print(f"Ingested {len(md_files)} policy files ({total_chunks} chunks) into '{store_path}'.")
    return vector_store

if __name__ == "__main__":
    ingest_finance_policies()

