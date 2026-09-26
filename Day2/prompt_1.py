import ollama
response=ollama.chat(
    model="llama3.2:3b",
    messages=[
        {
            "role":"user",
            "content":"What is machine learning in 9 lines"
        }
    ]
)
print(response["message"]["content"])