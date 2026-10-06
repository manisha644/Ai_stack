import streamlit as st
import ollama
import json

st.set_page_config(
    page_title="AI Flashcards",
    page_icon="🧠",
    layout="centered"
)

st.title("🧠 AI Flashcard Generator")
st.write("Learn any topic with simple and effective flashcards!")

topic = st.text_input(
    "📚 Enter your topic",
    placeholder="Example: Python loops"
)

number = st.slider(
    "🃏 Number of flashcards",
    1, 10, 5
)

if st.button("✨ Generate Flashcards"):

    if not topic.strip():
        st.warning("⚠️ Please enter a topic.")

    else:

        prompt = f"""
Create {number} useful study flashcards about {topic}.

Return ONLY valid JSON.

Format:
[
  {{
    "question": "Question",
    "importance": "Why this topic is important",
    "explanation": "Simple explanation",
    "key_points": ["Point 1", "Point 2", "Point 3"],
    "example": "Simple example"
  }}
]

Rules:
- Use very simple student-friendly language.
- Keep answers short.
- Give exactly 3 key points.
- If the topic is programming, include a small code example.
- If it is not programming, give a simple real-life example.
- Do not use markdown.
- Return only JSON.
"""

        with st.spinner("🧠 Creating your flashcards..."):

            try:

                response = ollama.chat(
                    model="llama3.2:3b",
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                )

                result = response["message"]["content"]

                cards = json.loads(result)

                st.success("🎉 Flashcards are ready!")

                for i, card in enumerate(cards, 1):

                    st.markdown("---")

                    st.subheader(
                        f"🃏 Flashcard {i}"
                    )

                    st.markdown(
                        f"### ❓ {card['question']}"
                    )

                    with st.expander("💡 Show Learning Details"):

                        st.markdown("### ⭐ Why is it important?")
                        st.write(card["importance"])

                        st.markdown("### 🧠 Simple Explanation")
                        st.write(card["explanation"])

                        st.markdown("### 📌 Key Points")

                        for point in card["key_points"]:
                            st.write(f"• {point}")

                        st.markdown("### 💻 Example")
                        st.code(card["example"])

            except json.JSONDecodeError:
                st.error("⚠️ Ollama did not return valid JSON.")

            except Exception as e:
                st.error("❌ Something went wrong.")
                st.code(str(e))