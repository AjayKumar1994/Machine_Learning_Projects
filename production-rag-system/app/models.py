from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    query: str = Field(min_length=1)
    session_id: str = "default"
    use_agents: bool = True


class Source(BaseModel):
    id: str
    title: str
    snippet: str
    score: float


class QueryResponse(BaseModel):
    answer: str
    sources: list[Source]
    trace: dict


class SearchRequest(BaseModel):
    query: str = Field(min_length=1)
    top_k: int = 5


class HealthResponse(BaseModel):
    status: str
    dependencies: dict[str, str]
