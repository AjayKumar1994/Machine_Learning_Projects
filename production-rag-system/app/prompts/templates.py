class PromptRegistry:
    def __init__(self):
        self._templates = {
            "answer": (
                "Use only provided sources. If insufficient evidence, state uncertainty clearly. "
                "Cite source ids in-line."
            ),
            "grader": "Score retrieval quality as correct/ambiguous/incorrect.",
        }

    def get(self, key: str) -> str:
        return self._templates[key]
