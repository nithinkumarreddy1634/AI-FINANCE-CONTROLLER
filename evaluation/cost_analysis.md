# AI Token Usage & Cost Optimization Report

Track 4: **AI Finance Controller** | Phase 5 Cost Benchmark

## 1. Token Usage Metrics

| Operation / Step | LLM Calls | Input Tokens | Output Tokens | Total Tokens | Est. Cost (USD) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Exact Match Reconciled** | 0 | 0 | 0 | 0 | **$0.000** |
| **Exception Investigation** | 1 | ~450 | ~150 | ~600 | **$0.0003** |
| **RAG Policy Query** | 0 (Local TF-IDF) | 0 | 0 | 0 | **$0.000** |
| **Tool Calculation** | 0 (Local Python) | 0 | 0 | 0 | **$0.000** |
| **500-Record Batch Run** | 300 | ~135,000 | ~45,000 | ~180,000 | **$0.090** |

---

## 2. Cost Optimization Strategies Applied

1. **Filtering Clean Matches**: Deterministic rules process exact matches instantly with 0 LLM calls, reducing API calls by **40%**.
2. **Local Vector Search**: RAG retriever uses zero-token local vector embeddings (`LocalVectorEmbedding`), avoiding external embedding API charges.
3. **Deterministic Tool Execution**: Calculations (`calculate_amount_difference`, `calculate_date_difference`) run in Python, preventing LLM math errors and token bloat.
4. **Concise Prompting**: Evidence packages format data in key-value pairs without filler text.

