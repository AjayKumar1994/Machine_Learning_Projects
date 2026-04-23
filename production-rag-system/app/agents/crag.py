from app.models import Source
from app.services.document_grader import DocumentGrader
from app.services.query_decomposer import QueryDecomposer


class CRAGAgent:
    def __init__(self):
        self.grader = DocumentGrader()
        self.decomposer = QueryDecomposer()

    def evaluate(self, query: str, docs: list[Source]) -> dict:
        quality, score = self.grader.grade(query, docs)
        actions: list[str] = []
        sub_queries: list[str] = []

        if quality == "ambiguous":
            actions.extend(["decompose", "re-retrieve", "merge"])
            sub_queries = self.decomposer.decompose(query)
        elif quality == "incorrect":
            actions.append("refuse_gracefully")

        return {
            "quality": quality,
            "score": score,
            "actions": actions,
            "sub_queries": sub_queries,
        }
