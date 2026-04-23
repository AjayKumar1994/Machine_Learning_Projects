from pathlib import Path


def extract_docx(path: Path) -> str:
    return f"[docx] extracted text from {path.name}"
