from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routes import health, query, search
from app.services.conversation import ConversationMemory
from app.services.rag_pipeline import RAGPipeline
from app.services.semantic_cache import SemanticCache

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_pipeline() -> RAGPipeline:
    return app.state.pipeline


@app.on_event("startup")
def startup() -> None:
    cache = SemanticCache(ttl_seconds=settings.semantic_cache_ttl_seconds)
    memory = ConversationMemory(window=settings.conversation_window)
    app.state.pipeline = RAGPipeline(cache=cache, memory=memory)


app.include_router(health.router)
app.include_router(search.router)
app.include_router(query.router)
