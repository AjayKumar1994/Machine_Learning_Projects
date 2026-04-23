from app.models import Source


class Reranker:
    """Cross-encoder reranking stub."""

    def rerank(self, query: str, candidates: list[Source], top_k: int = 5) -> list[Source]:
        return sorted(candidates, key=lambda c: c.score, reverse=True)[:top_k]
