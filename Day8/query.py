from sentence_transformers import SentenceTransformer
import chromadb
model = SentenceTransformer("all-MiniLM-L6-v2")
file_name = "ai_sample.txt"
with open(file_name, "r") as file:
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
# Embeddings
embeddings = model.encode(chunks)
# ChromaDB
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.create_collection(name="My_documents")
ids = []

for i in range(len(chunks)):
    ids.append(f"{file_name}_{i}")

collection.add(
    ids=ids,
    documents=chunks,
    embeddings=embeddings.tolist()
)
#Query phase
question="What is AI?"
question_embedding=model.encode(question)
results=collection.query(
    query_embeddings=[question_embedding.tolist()],
    n_results=3
)
retrieved_results=result['documents'][0]
retrieved_ids=results['ids'][0]