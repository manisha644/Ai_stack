import ollama 
msgs=[]
while True:
    question=input("You:")
    if question.lower()=="exit":
        break
    msgs.append(
        {"role":"user",
         "content":question}
    )
    response=ollama.chat(
        model="llama3.2:3b",
        messages=msgs)