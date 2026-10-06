import ollama
import streamlit as st

st.title("Welcome to my Chatbot App!!!")

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.header("File Upload")

    uploaded_file = st.file_uploader(
        "Upload a text file",
        type=["text"]
    )

    if uploaded_file is not None:
        content = uploaded_file.read().decode("utf-8")

        st.success("File uploaded!")
        st.write("File name:", uploaded_file.name)

        with st.expander("View File Content"):
            st.write(content)

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

question = st.chat_input("You:")

if question:
    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    with st.chat_message("user"):
        st.write(question)

    messages = st.session_state.messages.copy()

    if uploaded_file is not None:
        messages.insert(0, {
            "role": "system",
            "content": "Use this file content to answer the user's questions:\n" + content
        })

    with st.spinner("AI is thinking..."):
        response = ollama.chat(
            model="llama3.2:3b",
            messages=messages
        )

    answer = response["message"]["content"]

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer
    })

    with st.chat_message("assistant"):
        st.write(answer)
