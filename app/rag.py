from pathlib import Path


def load_faqs(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    return text

text = load_faqs(Path("data/faqs.txt"))
print(text)
