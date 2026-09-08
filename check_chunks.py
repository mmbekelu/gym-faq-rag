import chromadb

client = chromadb.PersistentClient(path="chroma_db")
collection = client.get_collection(name="gym_faqs")

data = collection.get(include=["documents"])
docs = data["documents"]

print(f"Total chunks: {len(docs)}")
for i, doc in enumerate(docs):
    print(i, len(doc))