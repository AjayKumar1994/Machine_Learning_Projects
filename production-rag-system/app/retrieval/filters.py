from app.models import Source


def metadata_filter(docs: list[Source], min_score: float = 0.1) -> list[Source]:
    return [d for d in docs if d.score >= min_score]
