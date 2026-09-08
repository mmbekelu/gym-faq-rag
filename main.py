from app.rag import retrieve, generation

while True:
    question = input("Question: ")
    docs = retrieve(question, 2)
    answer = generation(question, docs)
    print(answer)