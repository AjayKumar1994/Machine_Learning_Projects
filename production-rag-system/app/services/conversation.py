from collections import defaultdict, deque


class ConversationMemory:
    def __init__(self, window: int = 10):
        self.window = window
        self._history: dict[str, deque[dict]] = defaultdict(lambda: deque(maxlen=window))

    def add_turn(self, session_id: str, role: str, text: str) -> None:
        self._history[session_id].append({"role": role, "text": text})

    def get_context(self, session_id: str) -> list[dict]:
        return list(self._history[session_id])

    def rewrite_if_followup(self, query: str, session_id: str) -> str:
        history = self.get_context(session_id)
        if not history:
            return query
        last_user = next((t["text"] for t in reversed(history) if t["role"] == "user"), "")
        if query.lower().startswith(("and ", "what about", "also", "it ", "that ")):
            return f"{last_user} | follow-up: {query}"
        return query
