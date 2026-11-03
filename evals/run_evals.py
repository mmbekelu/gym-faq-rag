import json
from app.rag import process_question

with open("evals/questions.json", "r", encoding="utf-8") as file:
    questions = json.load(file)

print(len(questions))

evaluation_results = []

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

    

    if question["must_include"]:
        for include in question["must_include"]:
            evaluation_passed = evaluation_passed and include.lower() in result["answer"].lower()


    if question["must_not_include"]:
        for include in question["must_not_include"]:
            evaluation_passed = evaluation_passed and include.lower() not in result["answer"].lower()

    print(evaluation_passed)

    evaluation_record = {
        "id": question["id"],
    "passed": evaluation_passed,
    "answer": result["answer"],
    "refused": result["refused"],
    "source_found": source_found,
    "expected_faq_ids": question["expected_faq_ids"],
    "retrieved_chunk_ids": result["retrieved_chunk_ids"],
    "total_latency_ms": result["total_latency_ms"],
    "total_tokens": result["total_tokens"],
    "estimated_cost_usd": result["estimated_cost_usd"]
    }
    evaluation_results.append(evaluation_record)

with open("evals/results/baseline.json", "w", encoding="utf-8") as file:
    json.dump(evaluation_results, file, indent=4)