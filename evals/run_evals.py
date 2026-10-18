import json

with open("evals/questions.json", "r", encoding="utf-8") as file:
    questions = json.load(file)

print(len(questions))

for question in questions:
    print(question["id"])