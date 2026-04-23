from dataclasses import dataclass


@dataclass
class IndexedChunk:
    doc_id: str
    chunk_id: int
    text: str
    vector: list[float]


class InMemoryIndex:
    def __init__(self):
        self.items: list[IndexedChunk] = []

    def upsert(self, item: IndexedChunk) -> None:
        self.items.append(item)
