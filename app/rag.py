from pathlib import Path
import chromadb
from app.config import client


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

def index_chunks(chunks: list[str]) -> int:
    chroma_client = chromadb.PersistentClient(path="chroma_db")

    collection = chroma_client.get_or_create_collection(
    name="gym_faqs"
    )

    response = client.embeddings.create(
    model="text-embedding-3-small",
    input=chunks
    )

    embeddings = []

    for result in response.data:
        embeddings.append(result.embedding)


    ids = []

    for position in range(len(chunks)):
        current_id = f"faq-{position}"
        ids.append(current_id)

    collection.upsert(
    ids=ids,
    documents=chunks,
    embeddings=embeddings,
    )

    return len(chunks)