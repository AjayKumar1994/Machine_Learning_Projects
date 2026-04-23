from app.agents.adaptive_router import AdaptiveAgentRouter
from app.agents.crag import CRAGAgent
from app.agents.tools.code_search import CodeSearchTool
from app.agents.tools.vector_search import VectorSearchTool
from app.agents.tools.web_search import WebSearchTool
from app.models import QueryResponse, Source
from app.retrieval.filters import metadata_filter
from app.retrieval.reranker import Reranker
from app.security.content_filter import ContentFilter
from app.security.input_guard import InputGuard
from app.security.output_guard import OutputGuard
from app.services.conversation import ConversationMemory
from app.services.query_router import QueryRouter
from app.services.semantic_cache import SemanticCache


class RAGPipeline:
    def __init__(
        self,
        cache: SemanticCache,
        memory: ConversationMemory,
    ):
        self.cache = cache
        self.memory = memory

        self.input_guard = InputGuard()
        self.content_filter = ContentFilter()
        self.output_guard = OutputGuard()

        self.router = QueryRouter()
        self.agent_router = AdaptiveAgentRouter()
        self.vector_tool = VectorSearchTool()
        self.web_tool = WebSearchTool()
        self.code_tool = CodeSearchTool()

        self.reranker = Reranker()
        self.crag = CRAGAgent()

    def run(self, query: str, session_id: str = "default", use_agents: bool = True) -> QueryResponse:
        guard = self.input_guard.validate(query)
        if not guard.ok:
            return QueryResponse(answer=f"Request blocked: {guard.reason}", sources=[], trace={"blocked": True})

        rewritten_query = self.memory.rewrite_if_followup(query, session_id)

        cached = self.cache.get(rewritten_query)
        if cached:
            return QueryResponse(**cached)

        query_type = self.router.route(rewritten_query)
        tool_name = self.agent_router.choose(query_type)

        if tool_name == "web_search":
            candidates = self.web_tool.run(rewritten_query, top_k=7)
        elif tool_name == "code_search":
            candidates = self.code_tool.run(rewritten_query, top_k=7)
        else:
            candidates = self.vector_tool.run(rewritten_query, top_k=7)

        reranked = self.reranker.rerank(rewritten_query, metadata_filter(candidates), top_k=5)
        filtered = self.content_filter.filter_sources(reranked)

        crag_state = self.crag.evaluate(rewritten_query, filtered) if use_agents else {"quality": "correct"}
        answer = self._generate_answer(rewritten_query, filtered, crag_state)
        answer = self.output_guard.sanitize(answer)

        result = QueryResponse(
            answer=answer,
            sources=filtered,
            trace={
                "query_type": query_type,
                "tool": tool_name,
                "crag": crag_state,
                "cached": False,
            },
        )

        self.cache.set(rewritten_query, result.model_dump())
        self.memory.add_turn(session_id, "user", query)
        self.memory.add_turn(session_id, "assistant", result.answer)
        return result

    def _generate_answer(self, query: str, docs: list[Source], crag_state: dict) -> str:
        quality = crag_state.get("quality", "correct")
        if quality == "incorrect" or not docs:
            return "I could not find reliable evidence for this request. Please rephrase or provide more context."

        top = docs[0]
        citations = ", ".join(d.id for d in docs[:3])
        return (
            f"Based on retrieved context, the best answer to '{query}' is grounded in {top.title}. "
            f"Key evidence comes from sources: {citations}."
        )
