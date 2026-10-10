from app.rag import retrieve, generation
from openai import APITimeoutError, APIConnectionError, RateLimitError
import openai
import time
from datetime import datetime
import uuid
import logging
logging.basicConfig(level=logging.INFO)
logging.getLogger("httpx2").setLevel(logging.WARNING)

while True:
    question = input("Question: ")
    if not question.strip():
        print(ValueError("Enter your question please"))
        continue
    try:
        request_id = str(uuid.uuid4())
        start_time = time.perf_counter()
        docs, retrieved_chunk_ids, retrieval_scores, embedding_model, embedding_latency_ms, retrieval_latency_ms, embedding_tokens, upstream_request_id  = retrieve(question, 2)
        total_embedding_latency_ms = embedding_latency_ms
        total_embedding_tokens = embedding_tokens
        total_retrieval_latency_ms = retrieval_latency_ms
        upstream_request_ids = [upstream_request_id]
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
                        "estimated_embedding_cost_usd": embedding_cost
        }
        logging.info(request_record)
    except APITimeoutError as error:
        type_error = type(error).__name__
        error_record = {
            "event": "question_failed",
            "error_type": type_error,
            "request_id" : request_id
        }
        logging.error(error_record)
        print("The AI service took too long to respond. Please try again.")
        continue
    except APIConnectionError as error:
        type_error = type(error).__name__
        error_record = {
            "event": "question_failed",
            "error_type": type_error,
            "request_id" : request_id
        }
        logging.error(error_record)
        print("The AI service couldn't be reached. Please try again.")
        continue
    except RateLimitError as error:
        type_error = type(error).__name__
        error_record = {
            "event": "question_failed",
            "error_type": type_error,
            "request_id" : request_id
        }
        logging.error(error_record)
        print("The AI service hit a usage limit. Please try again later.")
        continue
    except openai.InternalServerError as error:
        type_error = type(error).__name__
        error_record = {
            "event": "question_failed",
            "error_type": type_error,
            "request_id" : request_id
        }
        logging.error(error_record)
        print("The AI service had a temporary server error. Please try again later.")