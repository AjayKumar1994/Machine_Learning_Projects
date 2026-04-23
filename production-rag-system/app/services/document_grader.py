from app.models import Source


class DocumentGrader:
    """CRAG-style retrieval quality grading."""

    def grade(self, query: str, docs: list[Source]) -> tuple[str, float]:
        if not docs:
            return "incorrect", 0.0
        avg = sum(d.score for d in docs) / len(docs)
        if avg >= 0.75:
            return "correct", avg
        if avg >= 0.35:
            return "ambiguous", avg
        return "incorrect", avg
