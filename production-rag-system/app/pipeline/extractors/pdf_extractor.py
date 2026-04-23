from pathlib import Path


def extract_pdf(path: Path) -> str:
    return f"[pdf] extracted text from {path.name}"
