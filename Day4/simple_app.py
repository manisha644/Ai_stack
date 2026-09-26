import streamlit as st

st.title("My First Streamlit App!!")

st.header("Welcome Section")

st.subheader("About My AI Application")

st.write("Welcome to My AI application!")

name = st.text_input("Enter your name:")

if st.button("Submit"):
    st.write("Hello", name)