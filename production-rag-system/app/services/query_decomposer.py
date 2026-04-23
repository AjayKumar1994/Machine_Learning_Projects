class QueryDecomposer:
    """Split complex compound questions into sub-queries."""

    separators = (" and ", ";", " then ", " also ")

    def decompose(self, query: str) -> list[str]:
        for sep in self.separators:
            if sep in query.lower():
                parts = [p.strip() for p in query.split(sep) if p.strip()]
                return parts if len(parts) > 1 else [query]
        return [query]
