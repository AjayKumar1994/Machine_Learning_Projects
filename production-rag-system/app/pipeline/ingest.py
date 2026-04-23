import argparse
from pathlib import Path

from app.pipeline.chunker import chunk_text
from app.pipeline.deduplicator import doc_hash
from app.pipeline.embedder import embed
from app.pipeline.extractors.docx_extractor import extract_docx
from app.pipeline.extractors.html_extractor import extract_html
from app.pipeline.extractors.image_extractor import extract_image
from app.pipeline.extractors.pdf_extractor import extract_pdf
from app.pipeline.extractors.text_extractor import extract_text
from app.pipeline.indexer import InMemoryIndex, IndexedChunk
from app.pipeline.preprocessor import preprocess


def choose_extractor(path: Path):
    ext = path.suffix.lower()
    if ext == ".pdf":
        return extract_pdf
    if ext in {".htm", ".html"}:
        return extract_html
    if ext == ".docx":
        return extract_docx
    if ext in {".png", ".jpg", ".jpeg", ".tiff"}:
        return extract_image
    return extract_text


def run_ingestion(input_dir: Path) -> InMemoryIndex:
    index = InMemoryIndex()
    seen: set[str] = set()

    for path in sorted(input_dir.rglob("*")):
        if not path.is_file():
            continue

        extractor = choose_extractor(path)
        text = preprocess(extractor(path))
        h = doc_hash(text)
        if h in seen:
            continue
        seen.add(h)

        for i, ch in enumerate(chunk_text(text)):
            index.upsert(IndexedChunk(doc_id=path.stem, chunk_id=i, text=ch, vector=embed(ch)))

    return index


def main() -> None:
    parser = argparse.ArgumentParser(description="Run offline ingestion pipeline")
    parser.add_argument("--input-dir", type=Path, required=True)
    args = parser.parse_args()

    index = run_ingestion(args.input_dir)
    print(f"Indexed chunks: {len(index.items)}")


if __name__ == "__main__":
    main()
