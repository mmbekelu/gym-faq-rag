from app.rag import retrieve, generation
from openai import APITimeoutError, APIConnectionError, RateLimitError
import openai
import time

while True:
    question = input("Question: ")
    if not question.strip():
        print(ValueError("Enter your question please"))
        continue
    try:
        start_time = time.perf_counter()
        docs = retrieve(question, 2)
        answer, generation_latency_ms, input_tokens, output_tokens, total_tokens = generation(question, docs)
        input_tokens_fallback = 0
        output_tokens_fallback = 0
        total_tokens_fallback = 0
        if answer == "I don’t have enough information in the gym FAQ to answer that.": 
            docs = retrieve(question, 20)
            answer, generation_latency_ms, input_tokens_fallback, output_tokens_fallback, total_tokens_fallback = generation(question, docs)
        end_time = time.perf_counter()
        total_request_latency = (end_time - start_time) * 1000
        print(answer, generation_latency_ms, total_request_latency, input_tokens + input_tokens_fallback, output_tokens + output_tokens_fallback, total_tokens + total_tokens_fallback) 
    except APITimeoutError:
        print("The AI service took too long to respond. Please try again.")
        continue
    except APIConnectionError:
        print("The AI service couldn't be reached. Please try again.")
        continue
    except RateLimitError:
        print("The AI service hit a usage limit. Please try again later.")
        continue
    except openai.InternalServerError:
        print("The AI service had a temporary server error. Please try again later.")