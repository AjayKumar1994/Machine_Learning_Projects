# Production RAG System (Template)

This folder provides a complete, runnable template for a **production-oriented RAG stack** based on your architecture plan:

- FastAPI runtime with streaming query endpoint
- Guardrails (input/content/output)
- Conversation memory + semantic cache
- Query router + hybrid retrieval + reranker + CRAG grading
- Agent loop for correction/decomposition
- Offline ingestion pipeline (extract -> preprocess -> chunk -> embed -> index)

## Quick start

```bash
cd production-rag-system
python -m venv .venv
source .venv/bin/activate
pip install -e .
uvicorn app.main:app --reload
```

Then open:
- `GET /health`
- `POST /api/search`
- `POST /api/query`

## Notes

- Retrieval and LLM calls are implemented with lightweight local stubs so the project runs immediately.
- Replace stubs in `app/retrieval/` and `app/services/rag_pipeline.py` with your provider integrations (Qdrant/Redis/LLM/etc.).
- Run offline indexing:

```bash
python -m app.pipeline.ingest --input-dir ./data/raw
```
