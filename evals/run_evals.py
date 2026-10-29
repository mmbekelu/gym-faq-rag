import json
from app.rag import process_question

with open("evals/questions.json", "r", encoding="utf-8") as file:
    questions = json.load(file)

print(len(questions))

for question in questions[:1]:
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
    else:
         print("Nothing")
         expected_id = None
    print(expected_id)
    source_found = False

    for document in result["retrieved_docs"]:
        if expected_id == None:
            pass
        else:
            if expected_id in document:
                source_found = True

    print(source_found)

    if question["expected_faq_ids"]:
        evaluation_passed = question["expected_refusal"] == result["refused"] and source_found
    else:
        evaluation_passed = question["expected_refusal"] == result["refused"]

    print(evaluation_passed)

    if question["must_include"]:
        for include in question["must_include"]:
            print(include in result["answer"])