from app.rag import retrieve, generation
from openai import APITimeoutError, APIConnectionError, RateLimitError
import openai

while True:
    question = input("Question: ")
    if not question.strip():
        print(ValueError("Enter your question please"))
        continue
    try:
        docs = retrieve(question, 2)
        answer, generation_latency_ms = generation(question, docs)
        if answer == "I don’t have enough information in the gym FAQ to answer that.": 
            docs = retrieve(question, 20)
            answer, generation_latency_ms = generation(question, docs)
        print(answer, generation_latency_ms) 
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