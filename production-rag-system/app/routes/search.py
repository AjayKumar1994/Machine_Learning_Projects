from fastapi import APIRouter, Depends

from app.models import SearchRequest
from app.services.rag_pipeline import RAGPipeline
from app.main import get_pipeline

router = APIRouter(prefix="/api/search", tags=["search"])


@router.post("")
def search(req: SearchRequest, pipeline: RAGPipeline = Depends(get_pipeline)) -> dict:
    result = pipeline.run(req.query, session_id="search", use_agents=False)
    return {
        "query": req.query,
        "hits": [s.model_dump() for s in result.sources[: req.top_k]],
        "trace": result.trace,
    }
