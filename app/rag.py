from pathlib import Path

def load_faqs(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    if not text.strip():
        raise ValueError("FAQ file is empty")
    return text
