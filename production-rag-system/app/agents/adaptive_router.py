class AdaptiveAgentRouter:
    """Select data source route: internal vector db, web, or code search."""

    def choose(self, query_type: str) -> str:
        mapping = {
            "vector": "vector_search",
            "web": "web_search",
            "code": "code_search",
        }
        return mapping.get(query_type, "vector_search")
