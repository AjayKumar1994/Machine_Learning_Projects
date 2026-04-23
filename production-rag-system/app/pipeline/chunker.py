def chunk_text(text: str, size: int = 500, overlap: int = 50) -> list[str]:
    if size <= overlap:
        raise ValueError("size must be greater than overlap")
    chunks = []
    start = 0
    while start < len(text):
        end = min(len(text), start + size)
        chunks.append(text[start:end])
        if end == len(text):
            break
        start = end - overlap
    return chunks
