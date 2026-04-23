class QueryRouter:
    """Classify query intent and choose retrieval strategy."""

    def route(self, query: str) -> str:
        q = query.lower()
        if any(k in q for k in ["latest", "today", "current"]):
            return "web"
        if any(k in q for k in ["code", "function", "repository", "class"]):
            return "code"
        return "vector"
