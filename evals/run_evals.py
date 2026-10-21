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

result = process_question(questions[0]["question"])
print(result["answer"])
print(questions[0]["expected_refusal"] == result["refused"])
print(questions[0]["category"])