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

## Test from Jupyter Notebook (local machine)

### 1) Install and start API

In a terminal:

```bash
cd production-rag-system
python -m venv .venv
source .venv/bin/activate
pip install -e .
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Keep this terminal running.

### 2) Open Jupyter

In a second terminal:

```bash
cd production-rag-system
source .venv/bin/activate
pip install notebook requests sseclient-py
jupyter notebook
```

### 3) Notebook cell: health check

```python
import requests

BASE_URL = "http://127.0.0.1:8000"
r = requests.get(f"{BASE_URL}/health", timeout=10)
print(r.status_code)
print(r.json())
```

Expected: `200` and a JSON payload with `status: ok`.

### 4) Notebook cell: search endpoint

```python
import requests

payload = {"query": "what is retrieval augmented generation?", "top_k": 3}
r = requests.post("http://127.0.0.1:8000/api/search", json=payload, timeout=20)
print(r.status_code)
print(r.json())
```

Expected: `200` with `hits` and `trace`.

### 5) Notebook cell: streaming query endpoint (SSE)

```python
import requests

payload = {
    "query": "Explain semantic cache in RAG",
    "session_id": "nb-session-1",
    "use_agents": True
}

with requests.post(
    "http://127.0.0.1:8000/api/query",
    json=payload,
    stream=True,
    timeout=30
) as r:
    print("status:", r.status_code)
    for line in r.iter_lines(decode_unicode=True):
        if line:
            print(line)
```

Expected: multiple `data:` lines followed by `event: done`.

### 6) Optional: test offline ingestion in notebook

```python
from pathlib import Path
from app.pipeline.ingest import run_ingestion

index = run_ingestion(Path("./data/raw"))
print("Indexed chunks:", len(index.items))
```

If Jupyter cannot import `app`, add:

```python
import sys
from pathlib import Path
sys.path.append(str(Path.cwd()))
```

## Notes

- Retrieval and LLM calls are implemented with lightweight local stubs so the project runs immediately.
- Replace stubs in `app/retrieval/` and `app/services/rag_pipeline.py` with your provider integrations (Qdrant/Redis/LLM/etc.).
- Run offline indexing:

```bash
python -m app.pipeline.ingest --input-dir ./data/raw
```
