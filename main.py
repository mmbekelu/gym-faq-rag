from app.rag import retrieve, generation

while True:
    question = input("Question: ")
    if not question.strip():
        print(ValueError("Enter your question please"))
        continue
    docs = retrieve(question, 2)
    answer = generation(question, docs)
    if answer == "I don’t have enough information in the gym FAQ to answer that.": 
        docs = retrieve(question, 20)
        answer = generation(question, docs)
    print(answer) 
