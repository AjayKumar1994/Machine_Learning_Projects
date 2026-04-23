from pathlib import Path


def extract_image(path: Path) -> str:
    return f"[image+ocr] extracted text from {path.name}"
