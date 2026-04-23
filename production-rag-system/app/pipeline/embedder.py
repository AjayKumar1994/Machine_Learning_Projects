import math


def embed(text: str, dim: int = 16) -> list[float]:
    base = sum(ord(c) for c in text)
    return [math.sin(base + i) for i in range(dim)]
