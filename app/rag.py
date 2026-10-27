from pathlib import Path
from app.config import client
import chromadb
import time
import uuid
from datetime import datetime

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

def retrieve(question: str, n_results: int) -> tuple[list[str], list[str], list[float], str, float, float, int, str | None]:
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
    upstream_request_id = response._request_id
    return documents, chunk_ids, retrieval_scores, embedding_model, embedding_latency_ms, retrieval_latency_ms, embedding_tokens, upstream_request_id

def generation(question: str, retrieved_strings: list[str]) -> tuple[str, float, int, int, int, str, str | None]:
    combined = " ".join(retrieved_strings)
    instructions = "Answer only using the retrieved FAQ context. If the context does not contain enough information to answer the question, reply exactly: 'I don’t have enough information in the gym FAQ to answer that.' Otherwise, answer using only the retrieved FAQ context and do not invent gym policy."
    input_text = f"Question:\n{question}\n\nRetrieved FAQ context:\n{combined}"
    start_time = time.perf_counter()
    response = client.responses.create(model="gpt-6-luna", instructions=instructions, input=input_text)
    end_time = time.perf_counter()
    generation_latency_ms = (end_time - start_time) * 1000
    llm_model = response.model
    generation_request_id = response._request_id
    return response.output_text, generation_latency_ms, response.usage.input_tokens, response.usage.output_tokens, response.usage.total_tokens, llm_model, generation_request_id

def process_question(question):
    request_id = str(uuid.uuid4())
    start_time = time.perf_counter()
    docs, retrieved_chunk_ids, retrieval_scores, embedding_model, embedding_latency_ms, retrieval_latency_ms, embedding_tokens, upstream_request_id  = retrieve(question, 2)
    upstream_request_ids = [upstream_request_id]
    total_embedding_latency_ms = embedding_latency_ms
    total_embedding_tokens = embedding_tokens
    total_retrieval_latency_ms = retrieval_latency_ms
    answer, generation_latency_ms, input_tokens, output_tokens, total_tokens, llm_model, generation_request_id = generation(question, docs)
    generation_request_ids = [generation_request_id]
    total_generation_latency_ms = generation_latency_ms
    fallback_used = False
    input_tokens_fallback = 0
    output_tokens_fallback = 0
    total_tokens_fallback = 0
    if answer == "I don’t have enough information in the gym FAQ to answer that.":
        docs, retrieved_chunk_ids, retrieval_scores, embedding_model, embedding_latency_ms_fallback, retrieval_latency_ms_fallback, embedding_tokens_fallback, upstream_request_id_fallback = retrieve(question, 20)
        upstream_request_ids.append(upstream_request_id_fallback)
        total_embedding_latency_ms += embedding_latency_ms_fallback
        total_embedding_tokens += embedding_tokens_fallback
        total_retrieval_latency_ms += retrieval_latency_ms_fallback
        answer, generation_latency_ms_fallback, input_tokens_fallback, output_tokens_fallback, total_tokens_fallback, llm_model,  generation_request_id_fallback = generation(question, docs)
        generation_request_ids.append(generation_request_id_fallback)
        total_generation_latency_ms += generation_latency_ms_fallback
        fallback_used = True
    end_time = time.perf_counter()
    total_request_latency = (end_time - start_time) * 1000
    input_price = 0.10
    output_price = 0.50
    input_cost = (input_tokens + input_tokens_fallback) / 1_000_000 * input_price
    output_cost = (output_tokens + output_tokens_fallback) / 1_000_000 * output_price
    estimated_generation_cost = input_cost + output_cost
    total_embedding_price = 0.02
    embedding_cost = (total_embedding_tokens) / 1_000_000 * total_embedding_price
    estimated_cost_usd = embedding_cost + estimated_generation_cost
    refused = answer == "I don’t have enough information in the gym FAQ to answer that."
    request_record = {"question": question,
                            "total_tokens": total_tokens + total_tokens_fallback,
                            "total_latency_ms": total_request_latency,
                            "estimated_generation_cost_usd": estimated_generation_cost,
                            "input_tokens": input_tokens + input_tokens_fallback,
                            "output_tokens": output_tokens + output_tokens_fallback,
                            "generation_latency_ms": total_generation_latency_ms,
                            "answer": answer,
                            "fallback_used": fallback_used,
                            "timestamp": datetime.now(),
                            "event_name": "question_completed",
                            "request_id": request_id,
                            "refused": refused,
                            "retrieved_chunk_ids": retrieved_chunk_ids,
                            "retrieval_scores": retrieval_scores,
                            "generation_model": llm_model,
                            "embedding_model": embedding_model,
                            "embedding_latency_ms": total_embedding_latency_ms,
                            "retrieval_latency_ms": total_retrieval_latency_ms,
                            "embedding_tokens": total_embedding_tokens,
                            "upstream_request_ids": upstream_request_ids,
                            "generation_request_ids": generation_request_ids,
                            "estimated_cost_usd": estimated_cost_usd,
                            "estimated_embedding_cost_usd": embedding_cost,
                            "retrieved_docs": docs
            }
    return request_record