from collections.abc import Iterator

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.main import get_pipeline
from app.models import QueryRequest
from app.services.rag_pipeline import RAGPipeline

router = APIRouter(prefix="/api/query", tags=["query"])


def sse_chunks(text: str) -> Iterator[str]:
    for token in text.split():
        yield f"data: {token}\\n\\n"
    yield "event: done\\ndata: [DONE]\\n\\n"


@router.post("")
def query(req: QueryRequest, pipeline: RAGPipeline = Depends(get_pipeline)) -> StreamingResponse:
    result = pipeline.run(req.query, session_id=req.session_id, use_agents=req.use_agents)
    payload = (
        f"ANSWER: {result.answer}\\n"
        f"SOURCES: {[s.id for s in result.sources]}\\n"
        f"TRACE: {result.trace}"
    )
    return StreamingResponse(sse_chunks(payload), media_type="text/event-stream")
