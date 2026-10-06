from sentence_transformers import SentenceTransformer
import chromadb

model = SentenceTransformer("all-MiniLM-L6-v2")

with open("ai_sample.txt", "r") as file:
    text = file.read()

print(text)

# Chunks
chunks = []

chunk_size = 35
chunk_overlap = 5
step = chunk_size - chunk_overlap

for i in range(0, len(text), step):
    chunk = text[i:i + chunk_size]
    chunks.append(chunk)

print("No of chunks:", len(chunks))

for i, chunk in enumerate(chunks):
    print(f"Chunk {i} -> {chunk}")

# Embeddings
embeddings = model.encode(chunks)

print("Embeddings created successfully")
print(embeddings[0])
print(embeddings.shape)

# ChromaDB
client = chromadb.Client()

collection = client.create_collection(name="My_documents")

print("Collection created successfully.")

ids = []

for i in range(len(chunks)):
    ids.append(str(i))

collection.add(
    ids=ids,
    documents=chunks,
    embeddings=embeddings.tolist()
)

print("No of collection:", collection.count())

col = collection.get(ids=["0"])

print(col)

results=collection.get()
for i in range(len(results["ids"])):
    print(f"ID: {results['ids'][i]} -> Chunk: {results['documents'][i]}")
