import time
from dataclasses import dataclass


@dataclass
class CacheEntry:
    value: dict
    expires_at: float


class SemanticCache:
    def __init__(self, ttl_seconds: int = 3600):
        self.ttl_seconds = ttl_seconds
        self._store: dict[str, CacheEntry] = {}

    @staticmethod
    def _key(query: str) -> str:
        return query.strip().lower()

    def get(self, query: str) -> dict | None:
        key = self._key(query)
        entry = self._store.get(key)
        if not entry:
            return None
        if entry.expires_at < time.time():
            self._store.pop(key, None)
            return None
        return entry.value

    def set(self, query: str, value: dict) -> None:
        key = self._key(query)
        self._store[key] = CacheEntry(value=value, expires_at=time.time() + self.ttl_seconds)
