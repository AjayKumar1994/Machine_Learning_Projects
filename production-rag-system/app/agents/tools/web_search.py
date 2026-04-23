from app.models import Source


class WebSearchTool:
    """Stub web retrieval tool. Replace with real provider integration."""

    def run(self, query: str, top_k: int = 5) -> list[Source]:
        return [
            Source(
                id=f"web-{i}",
                title=f"Web Result {i}",
                snippet=f"Recent web snippet for '{query}' (result {i}).",
                score=max(0.15, 0.82 - i * 0.15),
            )
            for i in range(top_k)
        ]
