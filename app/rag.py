from pathlib import Path

def load_faqs(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    if not text.strip():
        raise ValueError("FAQ file is empty")
    return text

def chunk_text(
    text: str,
    chunk_size: int,
    overlap: int,
) -> list[str]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0")
    if overlap < 0:
        raise ValueError("overlap must be 0 or greater")
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    chunks = []
    position = 0

    while position < len(text):
        end = position + chunk_size
        current_chunk = text[position:end]
        chunks.append(current_chunk)
        position += chunk_size - overlap
        if end >= len(text):
            break
    return chunks
