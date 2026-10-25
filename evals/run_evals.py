import json
from app.rag import process_question

with open("evals/questions.json", "r", encoding="utf-8") as file:
    questions = json.load(file)

print(len(questions))

for question in questions:
    print(question["id"])
    print(question["question"])
    print(question["expected_refusal"])
    print(question["expected_faq_ids"])
    result = process_question(question["question"])
    print(result["answer"])
    print(question["expected_refusal"] == result["refused"])
    print(question["category"])
    print(result["retrieved_docs"])
    if question["expected_faq_ids"]:
        expected_id = question["expected_faq_ids"][0]
        print("Nothing")
    print(expected_id)
    source_found = False

for document in result["retrieved_docs"]:
    if expected_id in document:
        source_found = True

print(source_found)
