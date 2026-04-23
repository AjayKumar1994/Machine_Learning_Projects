import re


class OutputGuard:
    """PII redaction guard for final answer text."""

    email_re = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}")

    def sanitize(self, text: str) -> str:
        return self.email_re.sub("[REDACTED_EMAIL]", text)
