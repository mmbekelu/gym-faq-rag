from pathlib import Path
from app.config import client
import chromadb
import time

def load_faqs(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    if not text.strip():
        raise ValueError("FAQ file is empty")
    return text

def chunk_text(text) -> list[str]: 
    parts = text.split("---")
    return parts


def index_chunks(chunks: list[str]) -> int:
    chroma_client = chromadb.PersistentClient(path="chroma_db")
    collection = chroma_client.get_or_create_collection(name="gym_faqs")
    response = client.embeddings.create(model="text-embedding-3-small", 
    input=chunks)
    embeddings = []
    for result in response.data:
        embeddings.append(result.embedding)
    ids = []
    for x in range(len(chunks)):
        x = f"faqs-{x}"
        ids.append(x)
    collection.upsert(ids=ids, documents=chunks, embeddings=embeddings)
    return len(chunks)

def retrieve(question: str, n_results: int) -> tuple[list[str], list[str], list[float], str, float, float, int]:
    if not question.strip():
        raise ValueError("question cannot be empty")
    if n_results <= 0:
        raise ValueError("n_results must be greater than 0")
    chroma_client = chromadb.PersistentClient(path="chroma_db")
    collection = chroma_client.get_collection(name="gym_faqs")
    start_time = time.perf_counter()
    response = client.embeddings.create(model="text-embedding-3-small", input=question)
    end_time = time.perf_counter()
    embedding_latency_ms = (end_time - start_time) * 1000
    question_embedding = response.data[0].embedding
    retrieval_start_time = time.perf_counter()
    results = collection.query(query_embeddings=[question_embedding], n_results=n_results, include=["documents", "distances"])
    retrieval_end_time = time.perf_counter()
    retrieval_latency_ms = (retrieval_end_time - retrieval_start_time) * 1000
    documents = results["documents"][0]
    chunk_ids = results["ids"][0]
    retrieval_scores = results["distances"][0]
    embedding_model = response.model
    embedding_tokens = response.usage.total_tokens
    return documents, chunk_ids, retrieval_scores, embedding_model, embedding_latency_ms, retrieval_latency_ms, embedding_tokens

def generation(question: str, retrieved_strings: list[str]) -> tuple[str, float, int, int, int, str]:
    combined = " ".join(retrieved_strings)
    instructions = "Answer only using the retrieved FAQ context. If the context does not contain enough information to answer the question, reply exactly: 'I don’t have enough information in the gym FAQ to answer that.' Otherwise, answer using only the retrieved FAQ context and do not invent gym policy."
    input_text = f"Question:\n{question}\n\nRetrieved FAQ context:\n{combined}"
    start_time = time.perf_counter()
    response = client.responses.create(model="gpt-6-luna", instructions=instructions, input=input_text)
    end_time = time.perf_counter()
    generation_latency_ms = (end_time - start_time) * 1000
    llm_model = response.model
    return response.output_text, generation_latency_ms, response.usage.input_tokens, response.usage.output_tokens, response.usage.total_tokens, llm_model