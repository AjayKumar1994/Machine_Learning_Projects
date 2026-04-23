from dataclasses import dataclass


@dataclass
class GuardResult:
    ok: bool
    reason: str = ""


class InputGuard:
    """Simple deny-first prompt-injection detector."""

    blocked_patterns = (
        "ignore previous instructions",
        "reveal system prompt",
        "exfiltrate",
        "bypass security",
    )

    def validate(self, query: str) -> GuardResult:
        q = query.lower()
        for pattern in self.blocked_patterns:
            if pattern in q:
                return GuardResult(False, f"Blocked pattern detected: {pattern}")
        return GuardResult(True)
