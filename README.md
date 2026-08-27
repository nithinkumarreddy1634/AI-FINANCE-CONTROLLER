# AI-Powered Payment Reconciliation & Finance Controller

**Track 4: AI Finance Controller | Razorpay AI Builder Internship 2026**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-emerald.svg)](https://fastapi.tiangolo.com/)
[![Phase 4 Product UI](https://img.shields.io/badge/Phase%204-Fintech%20Product%20UI-blue.svg)]()
[![Tests](https://img.shields.io/badge/tests-36%20passing-brightgreen.svg)]()

---

## Executive Summary

The **AI-Powered Payment Reconciliation & Finance Controller** is a production-grade automated reconciliation platform. It ingests financial transactions across three primary records—**Customer Orders**, **Payment Gateway Logs**, and **Bank Settlement Statements**—to automatically detect matches, investigate exceptions, flag discrepancies, assign confidence scores, and maintain an immutable audit trail.

The application combines:
1. **Phase 1: Deterministic Engine**: High-speed, explainable rule matching across strong identifiers, amounts, dates, and references.
2. **Phase 2: AI Finance Controller Agent**: Evidence-backed LLM exception investigation, confidence policy thresholds, and human-in-the-loop review.
3. **Phase 3: RAG Engine & Tool Agent**: Policy RAG vector search over 7 finance policy documents, controlled agent tools, multi-signal candidate matching, step-by-step investigation timelines, post-LLM rule validation, and 3-way comparative benchmarks.
4. **Phase 4: Professional Fintech Product UI**: Complete Single-Page Application (SPA) featuring Sidebar Navigation, Topbar Search, Operations KPI Grid, 4 Visual Charts, Transaction Explorer with multi-column sorting/pagination, Prioritized Exception Risk Queue, Exception Investigation Modal, 1-Click Demo Pipeline Stepper, Report Exporter (CSV/JSON), Immutable Audit Logs Viewer, and System Health status indicators.

---

## Complete User Journey & System Architecture

```text
               Financial Datasets (CSVs / Uploads)
                               │
                               ▼
            Deterministic Reconciliation Engine (Phase 1)
                               │
                               ▼
                     Exception Risk Queue
                               │
            ┌──────────────────┴──────────────────┐
            ▼                                     ▼
   Policy RAG Retriever                 Controlled Agent Tools
(Vector Store over Policies)           (get_order, calculate_diff)
            │                                     │
            └──────────────────┬──────────────────┘
                               │
                               ▼
               AI Finance Controller Agent (Phase 2 & 3)
                               │
                               ▼
             Post-LLM Deterministic Rule Validator
      (Rejects Hallucinations & Amount Discrepancy Matches)
                               │
            ┌──────────────────┼──────────────────┐
            ▼                  ▼                  ▼
     AUTO_RECONCILE     MARK_FOR_REVIEW       ESCALATE
       (≥90 Conf)        (70-89 Conf)        (<70 Conf)
            │                  │                  │
            ▼                  ▼                  ▼
      Auto-Verified      Human Review Form    Senior Audit
                        (Approve / Reject)
                               │
                               ▼
                    Immutable Audit Trail Ledger
                               │
                               ▼
              Fintech Operations Dashboard (Phase 4 UI)
               (8 Views, Charts, Reports, Explorer)
```

---

## Product UI Views & Features

| View | Access Path | Key Features |
| :--- | :--- | :--- |
| **📊 Dashboard** | `View 1` | 10 Real Backend KPI Cards, 4 Visual Charts (Status Donut, Category Bar, Daily Volume Line, 3-Way Benchmark Bar). |
| **💳 Transactions** | `View 2` | Full Transaction Explorer with Multi-Column Sorting (`Order ID`, `Amount`, `Status`, `Confidence`), Search, Status/Date Filters, 10-per-page Pagination. |
| **🚨 Exception Center** | `View 3` | Prioritized Exception Queue categorizing risks into `CRITICAL` (≥₹10k), `HIGH` (₹2k-₹9.9k), `MEDIUM` (Mismatches), `LOW` (Typos/Lag). |
| **🤖 AI Investigations** | `View 4` | Dedicated AI Investigation Center with confidence filter pills and direct detail inspection. |
| **⚡ Reconciliation** | `View 5` | Custom CSV dataset upload (`orders.csv`, `payments.csv`, `bank_transactions.csv`) + **⚡ 1-Click Complete Synthetic Demo Pipeline** with live progress stepper. |
| **📄 Reports** | `View 6` | Instant download of exportable reports (Summary, Exceptions, AI Investigations, Audit Trail) in CSV and JSON formats. |
| **📝 Audit Logs** | `View 7` | Immutable audit trail table recording timestamps, transaction IDs, actors (`Rule Engine`, `AI Agent`, `Human Auditor`), decisions, confidence scores, and reviewer notes. |
| **⚙️ Settings & Health** | `View 8` | Configurable date tolerance windows, confidence policy thresholds, and live component health status indicators (`● AI Controller Online`, `● DB Connected`, `● RAG Ready`). |

---

## Interactive Exception Investigation Modal

When opening any exception, the **AI Investigation Center Modal** presents:
1. **Financial Comparison & Evidence Cards**: Side-by-side Order, Gateway Payment, and Bank Settlement evidence.
2. **Multi-Signal Candidate Ranking**: Scores candidate settlements using Identifier (40%), Amount (35%), Temporal (15%), and Text (10%) similarity.
3. **Retrieved Policy RAG Citations**: Section-level citations from `knowledge_base/` Markdown documents.
4. **AI Reasoning & Decision**: AI decision, confidence score gauge, recommended action, and human-readable summary.
5. **Step-by-Step Timeline**: Microsecond investigation log tracking tool calls and processing steps.
6. **Post-LLM Rule Validation Badge**: `VALIDATED BY RULE` or `REJECTED BY RULE`.
7. **Human-in-the-Loop Audit Form**: Action buttons (`APPROVED`, `REJECTED`, `MODIFIED`), Reviewer Name, and Reviewer Note textarea.

---

## 3-Way Comparative Benchmark Metrics

```text
Total Processed Records        : 120
Phase 1 Rule Matched Records   : 55 (45.83% Match Rate)
Phase 1 Exception Records      : 65
AI Exception Investigations    : 58 (Clean MATCHED records filtered out)

RAG Retrieval Success Rate     : 100.0%
AI Resolution Rate             : 45.83% (Rule matched + AI policy verified)
AI False Match Rate            : 0.0% (0 False Matches - 100% Guardrail Compliance)
Overall System Accuracy        : 94.17%
Average Response Latency       : 12.5 ms
Average Tool Calls / Inv       : 2.1 calls
```

---

## Quick Start Guide

### 1. Installation
```bash
git clone https://github.com/your-username/ai-finance-controller.git
cd ai-finance-controller

python -m pip install -r requirements.txt
```

### 2. Ingest Knowledge Base Policies & Generate Datasets
```bash
python -m knowledge.ingestion
python data/generator.py
python data/demo_scenarios_p3.py
```

### 3. Run Full Automated Test Suite (36 Tests)
```bash
python -m pytest -v
```

All 36 unit, safety, policy, audit, RAG, candidate matcher, and UI endpoint tests will pass.

### 4. Launch Application Server & Visual Product Dashboard
```bash
python -m uvicorn backend.main:app --reload
```

- 📊 **Product UI Dashboard**: [http://localhost:8000/](http://localhost:8000/)
- 📖 **Interactive Swagger API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## Key REST API Endpoints

### Phase 1 & 4 Core Endpoints
- `GET /health` — Health check endpoint.
- `POST /reconcile` — Execute deterministic reconciliation engine or process uploaded CSVs.
- `GET /summary` — Retrieve summary KPI metrics.
- `GET /transactions` — Filter, search, and list processed transactions.
- `GET /exceptions` — Retrieve exception records.

### Phase 2 & 3 AI Agent & RAG Endpoints
- `POST /api/v1/ai/investigate-all` — Batch investigate exceptions using AI Agent.
- `POST /api/v1/ai/investigate/{id}` — Investigate specific transaction.
- `GET /api/v1/ai/investigations` — Retrieve AI investigation results.
- `POST /api/v1/ai/investigations/{id}/review` — Submit Human Review Action (`APPROVED`, `REJECTED`, `MODIFIED`).
- `GET /api/v1/ai/metrics` — Retrieve 3-way comparative benchmark metrics.
- `POST /agent/rebuild-knowledge-base` — Rebuild policy RAG vector index.
- `GET /agent/investigations/{id}/timeline` — Retrieve step-by-step investigation timeline.

### Phase 4 Exportable Report Endpoints
- `GET /api/v1/reports/summary/csv` & `/json` — Export Reconciliation Summary Report.
- `GET /api/v1/reports/exceptions/csv` & `/json` — Export Exceptions Risk Ledger.
- `GET /api/v1/reports/ai-investigations/csv` & `/json` — Export AI Investigations Report.
- `GET /api/v1/reports/audit/csv` & `/json` — Export Immutable Audit Trail.
#   A I - F i n a n c e - c o n t r o l l e r  
 #   A I - F i n a n c e - c o n t r o l l e r  
 #   A I - F I N A N C E - C O N T R O L L E R  
 