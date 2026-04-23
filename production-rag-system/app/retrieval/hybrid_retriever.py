from app.models import Source


class HybridRetriever:
    """Dense + sparse retrieval stub, returned as fused candidates."""

    def retrieve(self, query: str, top_k: int = 5) -> list[Source]:
        return [
            Source(
                id=f"doc-{i}",
                title=f"Candidate {i}",
                snippet=f"Relevant passage for '{query}' from candidate {i}.",
                score=max(0.1, 0.9 - (i * 0.12)),
            )
            for i in range(top_k)
        ]
