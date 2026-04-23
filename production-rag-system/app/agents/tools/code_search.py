from app.models import Source


class CodeSearchTool:
    """Stub repository search tool. Replace with MCP/Git provider integration."""

    def run(self, query: str, top_k: int = 5) -> list[Source]:
        return [
            Source(
                id=f"code-{i}",
                title=f"Code Match {i}",
                snippet=f"Code-level retrieval hit for '{query}' (match {i}).",
                score=max(0.1, 0.76 - i * 0.1),
            )
            for i in range(top_k)
        ]
