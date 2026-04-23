from app.models import Source
from app.retrieval.hybrid_retriever import HybridRetriever


class VectorSearchTool:
    def __init__(self):
        self.retriever = HybridRetriever()

    def run(self, query: str, top_k: int = 5) -> list[Source]:
        return self.retriever.retrieve(query, top_k=top_k)
