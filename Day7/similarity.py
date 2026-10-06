from sentence_transformers import util,SentenceTransformer
model=SentenceTransformer("all-MiniLM-L6-v2")
sentences=[
    "I love Plaaying foootball",
    "I enjoy playing soccer",
    "I like eating pizza" 
]
sentence_embedding =model.encode(sentences)
print(sentence_embedding[0])
similarity1=util.cos_sim(sentence_embedding[0], sentence_embedding[1])
print(similarity1.item())