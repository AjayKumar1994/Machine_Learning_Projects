# Full-Fledged AI Agent System Design for Business Q&A on SQLite Data

## 1) Problem Definition
You have a SQLite database (~80 tables) containing invoicing, inventory, customers, payments, and related business activity. You want a conversational AI assistant that lets each business owner ask natural-language questions such as:

- “What was my total sales last month?”
- “Which products are low in stock and not reordered?”
- “Who are my top 10 customers by revenue this quarter?”
- “How many invoices are overdue by more than 30 days?”

The system should return **accurate, explainable, and secure** answers while respecting user-level data boundaries.

---

## 2) Target Capabilities

### Core capabilities
1. Natural language to SQL across complex schema.
2. Multi-turn memory (follow-up questions like “show only unpaid ones”).
3. KPI and trend analytics (sales, margin, inventory turnover, AR aging).
4. Chart-ready outputs (time series, category splits, top-N).
5. Explainability: show query logic and confidence.
6. Role-aware access control (owner/accountant/staff views).

### Advanced capabilities
1. Proactive insights (alerts for stockout risk, overdue receivables).
2. Forecasting (demand and cashflow projections).
3. Action suggestions (“create reorder draft for these SKUs”).
4. Document-grounded responses from policy/help docs (RAG).

---

## 3) High-Level Architecture

```text
User (Web/App/WhatsApp)
   │
   ▼
API Gateway + Auth (JWT/OAuth, tenant scoping)
   │
   ▼
AI Orchestrator (Agent Runtime)
   ├── Intent Router (analytics, operational, help/policy)
   ├── Conversation Memory Store
   ├── Semantic Layer Service
   ├── SQL Generation & Validation Module
   ├── Tool Executor (read-only DB, charting, exports)
   └── Guardrails (PII masking, policy checks, hallucination checks)
   │
   ├── SQLite/Replicated OLAP DB (query endpoint)
   ├── Metadata Catalog (tables, columns, joins, business glossary)
   ├── Vector Store (docs, schema descriptions, query examples)
   └── Observability (logs, traces, cost, query metrics)
```

---

## 4) Data Layer Design (Most Important)

SQLite is good for transactional workloads, but conversational analytics at scale is safer with a read-optimized layer.

### Recommended approach
1. Keep SQLite as source of truth for app writes.
2. Create a **read-only analytics replica** (DuckDB/Postgres/BigQuery/Snowflake based on budget).
3. ETL/ELT every N minutes (or CDC if available).
4. Agent queries analytics replica, not production write DB.

### Why
- Prevent lock/contention on production.
- Improve response time and concurrency.
- Allow materialized views and denormalized marts.

---

## 5) Semantic Layer (Required for Accuracy)

With 80 tables, direct NL→SQL is brittle. Introduce a semantic layer with:

1. **Business entities**: invoice, customer, item, payment, vendor, stock movement.
2. **Canonical metrics**:
   - gross_sales
   - net_sales
   - overdue_amount
   - inventory_value
   - gross_margin
3. **Curated joins** and join cardinality.
4. **Time dimensions** (invoice_date, due_date, payment_date).
5. **Synonyms** (e.g., “bill” = invoice, “product” = item).

Store this metadata in YAML/JSON and expose as context to the LLM.

---

## 6) Agent Workflow (Query Lifecycle)

1. User question received.
2. Intent router classifies: analytics / operational / doc-help.
3. Context builder fetches:
   - tenant/user permissions,
   - semantic model snippets,
   - prior conversation state,
   - relevant examples from vector store.
4. LLM drafts SQL against approved schema only.
5. SQL validator checks:
   - read-only enforcement,
   - forbidden tables/columns,
   - tenant filter is present,
   - complexity/time limits.
6. Query executor runs SQL on analytics DB.
7. Result interpreter returns:
   - concise answer,
   - table/chart data,
   - explanation (“how this was computed”).
8. Feedback logger captures success/failure for continuous improvement.

---

## 7) Multi-Tenant Security & Privacy

### Must-have controls
1. Row-level tenant isolation (`tenant_id` always injected).
2. Role-based controls for sensitive fields (cost price, salaries, tax IDs).
3. PII masking/tokenization in logs.
4. Encrypted data at rest and in transit.
5. Audit logs for every question, SQL, and result metadata.

### Guardrail strategy
- LLM cannot execute raw SQL directly.
- Only allow generated SQL through policy engine.
- Block DDL/DML (`INSERT`, `UPDATE`, `DELETE`, `DROP`, etc.).
- Set per-query timeout and result row limits.

---

## 8) Prompting Strategy

Use structured prompts with strict output schema:

- System prompt: business assistant rules and safety constraints.
- Developer prompt: schema + semantic metrics + SQL policy.
- User prompt: natural-language question.

Require model output in JSON:

```json
{
  "intent": "analytics",
  "sql": "SELECT ...",
  "confidence": 0.88,
  "assumptions": ["..."],
  "visualization": "line_chart"
}
```

If confidence is low or ambiguity detected, ask a clarifying question before executing.

---

## 9) RAG for Help/Policy Questions

For questions like “How is GST calculated?” or “What does invoice status overdue mean?” use document retrieval:

1. Ingest product docs, accounting rules, SOPs.
2. Chunk and embed into vector DB.
3. Retrieve top-k passages and answer with citations.

Keep SQL agent and doc-RAG agent separate, then orchestrate through intent router.

---

## 10) Observability, QA, and Evaluation

### Offline evaluation set
Create 300–500 benchmark questions:
- 40% revenue & invoice analytics
- 30% inventory analytics
- 20% receivables/payables
- 10% edge cases/ambiguous

Track:
1. SQL correctness (% exact/semantically correct).
2. Answer correctness (human-verified).
3. Latency (p50/p95).
4. Clarification rate.
5. Guardrail violation rate.

### Online monitoring
- query failures,
- empty result frequency,
- token and infra cost per question,
- user feedback thumbs up/down.

---

## 11) Suggested Tech Stack

### Backend
- Python + FastAPI
- Orchestrator: LangGraph / custom state machine
- SQL parser/validator: sqlglot + custom policy checks
- Task queue: Celery / RQ for async jobs

### Data
- Source: SQLite
- Analytics: DuckDB (small-mid) or Postgres (multi-user) or cloud DWH (large)
- Transformation: dbt

### AI
- LLM for reasoning and SQL generation
- Embedding model + vector DB (pgvector/FAISS/Weaviate)
- Optional reranker for better retrieval quality

### Frontend
- Chat UI with drill-down tables/charts
- “Show SQL” toggle for transparency
- Export CSV/XLSX

---

## 12) Phased Delivery Plan

### Phase 1 (2–4 weeks): Foundation
1. Schema introspection and semantic model v1.
2. Read-only SQL agent with guardrails.
3. Basic chat interface for top 20 business questions.
4. Audit logging and monitoring dashboard.

### Phase 2 (3–6 weeks): Production hardening
1. Role-aware access and row-level security.
2. Query caching and materialized KPIs.
3. Benchmark suite + automated regression checks.
4. Human feedback loop for failed/incorrect answers.

### Phase 3 (4–8 weeks): Advanced intelligence
1. Forecasting and anomaly alerts.
2. Action-taking workflows (reorder suggestions, reminder drafts).
3. Multilingual support and voice input.
4. Personalized proactive insights.

---

## 13) Example User Journeys

1. **Revenue analysis**
   - User: “Compare this month sales with last month by category.”
   - Agent: Returns table + bar chart + variance percentages.

2. **Inventory risk**
   - User: “Which SKUs may stock out in next 14 days?”
   - Agent: Uses sales velocity + current stock + lead time.

3. **Collections management**
   - User: “List customers with overdue amount above 50,000 and draft reminder message.”
   - Agent: Produces list + suggested communication text.

---

## 14) Non-Functional Targets

- p95 latency < 5s for common queries.
- Accuracy > 90% on curated benchmark.
- 99.9% read availability.
- Strict tenant isolation with zero leakage incidents.

---

## 15) Implementation Checklist

1. [ ] Build schema catalog from SQLite.
2. [ ] Define semantic entities, metrics, and join paths.
3. [ ] Stand up read-only analytics endpoint.
4. [ ] Implement agent with tool-calling and SQL validator.
5. [ ] Add RBAC + tenant filters + audit logs.
6. [ ] Build benchmark dataset and evaluation harness.
7. [ ] Launch pilot with limited users and iterate.

---

## 16) Practical Recommendation

For fastest success: start with **narrow scope** (sales + invoices + inventory summary), enforce strict guardrails, and heavily invest in semantic modeling and evaluation. In enterprise analytics assistants, these two components matter more than choosing a specific model provider.
