from app.models import Source


class ContentFilter:
    """Document-side quality checks and lightweight policy filtering."""

    def filter_sources(self, sources: list[Source]) -> list[Source]:
        # Extend with policy labels, malware checks, trust ranking, etc.
        return [s for s in sources if s.score >= 0.05]
