import streamlit as st
import ollama
import chromadb
from sentence_transformers import SentenceTransformer
from datetime import datetime


# --------------------------------------------------
# PAGE SETTINGS
# --------------------------------------------------

st.set_page_config(
    page_title="HomeFix AI",
    page_icon="🏠",
    layout="wide"
)


# --------------------------------------------------
# EMBEDDING MODEL
# --------------------------------------------------

@st.cache_resource
def load_embedding_model():
    return SentenceTransformer("all-MiniLM-L6-v2")


model = load_embedding_model()


# --------------------------------------------------
# CHROMADB
# --------------------------------------------------

@st.cache_resource
def load_chroma():

    client = chromadb.PersistentClient(
        path="./homefix_db"
    )

    collection = client.get_or_create_collection(
        name="homefix"
    )

    return collection


collection = load_chroma()


# --------------------------------------------------
# KNOWLEDGE DATA
# --------------------------------------------------

knowledge = [

    "A leaking tap can be caused by a worn washer, loose connection, damaged seal, or another plumbing problem. For persistent problems contact a qualified plumber.",

    "Slow drainage can happen because of a blockage or accumulated debris. Basic cleaning of the visible drain area may help. Persistent blockages should be handled by a plumber.",

    "A light that is not working can have several causes including a bulb problem, switch problem, or electrical fault. Do not touch exposed wires. Contact a qualified electrician for electrical faults.",

    "If an electrical switch or socket becomes unusually hot, stop using it and contact a qualified electrician. Do not open electrical components yourself.",

    "A refrigerator that is not cooling properly can have several causes. Check that the appliance has power and that airflow areas are not blocked. For persistent problems contact an appliance technician.",

    "An air conditioner may perform poorly because of a dirty filter, airflow problem, or technical fault. Basic filter cleaning may help. Contact a qualified technician for technical problems.",

    "A noisy door may have a hinge or alignment problem. Visible inspection of the hinge area may help identify the problem. Damaged hardware should be handled by a suitable professional.",

    "Bad kitchen odors can come from food waste, drains, bins, or dirty surfaces. Cleaning the area and removing waste regularly can help.",

    "Regular home maintenance includes checking visible water leaks, cleaning appliance filters, checking for damage, and keeping important areas clean.",

    "Home electrical repairs can be dangerous. Do not work with exposed wires or open electrical equipment. Contact a qualified electrician.",

    "Gas-related problems can be dangerous. Do not attempt to repair gas equipment yourself. Move away from danger and contact the appropriate qualified service.",

    "Water near electrical equipment can be dangerous. Avoid contact with electrical equipment in wet areas and seek professional help when necessary."
]


# --------------------------------------------------
# ADD KNOWLEDGE TO CHROMADB
# --------------------------------------------------

if collection.count() == 0:

    embeddings = model.encode(
        knowledge
    ).tolist()

    ids = []

    for i in range(len(knowledge)):
        ids.append("knowledge_" + str(i))

    collection.add(
        documents=knowledge,
        embeddings=embeddings,
        ids=ids
    )


# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "history" not in st.session_state:
    st.session_state.history = []

if "maintenance" not in st.session_state:

    st.session_state.maintenance = [
        ["🚰 Check water leaks", False],
        ["❄️ Clean AC filter", False],
        ["🧼 Clean refrigerator", False],
        ["💡 Check damaged switches", False],
        ["🪟 Clean windows", False]
    ]


# --------------------------------------------------
# SEARCH CHROMADB
# --------------------------------------------------

def search_knowledge(question):

    question_embedding = model.encode(
        [question]
    ).tolist()

    result = collection.query(
        query_embeddings=question_embedding,
        n_results=3
    )

    if result["documents"]:
        return result["documents"][0]

    return []


# --------------------------------------------------
# ASK OLLAMA
# --------------------------------------------------

def ask_ai(question, context):

    prompt = f"""
You are HomeFix AI.

You help users understand common home-maintenance problems.

IMPORTANT:
- Give general information only.
- Do not give dangerous repair instructions.
- Do not tell users to work with exposed wires.
- Do not tell users to repair gas systems.
- If a problem is dangerous, recommend a qualified professional.
- Keep the answer simple.

Relevant HomeFix knowledge:

{context}

User problem:

{question}

Answer using these headings:

🔍 Possible Problem

💡 Possible Causes

✅ Safe Basic Checks

🛠️ When to Contact a Professional

⚠️ Safety Note
"""

    response = ollama.chat(
        model="llama3.2:3b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response["message"]["content"]


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

st.sidebar.title("🏠 HomeFix AI")

st.sidebar.write(
    "AI-Powered Home Problem Assistant"
)

page = st.sidebar.radio(
    "Choose a page",
    [
        "🏠 Dashboard",
        "🤖 AI Assistant",
        "🔧 Categories",
        "📚 Knowledge Base",
        "📋 Problem History",
        "🛠️ Maintenance",
        "⚠️ Safety Center"
    ]
)

st.sidebar.success(
    "🤖 Model: llama3.2:3b"
)


# ==================================================
# DASHBOARD
# ==================================================

if page == "🏠 Dashboard":

    st.title("🏠 HomeFix AI")

    st.subheader(
        "Understand your home problems. Maintain your home better."
    )

    st.write(
        "HomeFix AI uses Ollama, ChromaDB and "
        "Sentence Transformers to provide "
        "AI-powered information about common "
        "household problems."
    )

    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "📚 Knowledge",
            collection.count()
        )

    with col2:
        st.metric(
            "📋 Problems Checked",
            len(st.session_state.history)
        )

    with col3:
        st.metric(
            "🛠️ Maintenance Tasks",
            len(st.session_state.maintenance)
        )

    st.divider()

    st.subheader("🔧 Home Problems")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.info("🚰 Plumbing")

    with c2:
        st.info("💡 Electrical")

    with c3:
        st.info("❄️ Appliances")

    with c4:
        st.info("🚪 Home Repairs")

    st.divider()

    st.subheader("✨ How HomeFix AI Works")

    st.write(
        "1️⃣ Describe your home problem"
    )

    st.write(
        "2️⃣ ChromaDB searches relevant knowledge"
    )

    st.write(
        "3️⃣ Ollama analyzes the information"
    )

    st.write(
        "4️⃣ HomeFix AI gives a simple answer"
    )


# ==================================================
# AI ASSISTANT
# ==================================================

elif page == "🤖 AI Assistant":

    st.title("🤖 HomeFix AI Assistant")

    st.write(
        "Describe your household problem below."
    )

    category = st.selectbox(
        "🔧 Select Category",
        [
            "General",
            "Plumbing",
            "Electrical",
            "Appliances",
            "Doors & Windows",
            "Cleaning",
            "Maintenance"
        ]
    )

    question = st.text_area(
        "📝 What is the problem?",
        placeholder="Example: My kitchen tap is leaking."
    )

    if st.button(
        "🤖 Ask HomeFix AI",
        use_container_width=True
    ):

        if question.strip() == "":

            st.warning(
                "Please describe your problem."
            )

        else:

            with st.spinner(
                "🔎 Searching HomeFix knowledge..."
            ):

                results = search_knowledge(
                    question
                )

            context = "\n\n".join(results)

            with st.spinner(
                "🤖 Ollama is thinking..."
            ):

                try:

                    answer = ask_ai(
                        question,
                        context
                    )

                    st.success(
                        "✅ Analysis completed"
                    )

                    st.markdown(answer)

                    st.session_state.history.append(
                        {
                            "problem": question,
                            "category": category,
                            "answer": answer,
                            "date": datetime.now().strftime(
                                "%d-%m-%Y %H:%M"
                            )
                        }
                    )

                except Exception as e:

                    st.error(
                        "❌ Ollama error"
                    )

                    st.write(str(e))


# ==================================================
# CATEGORIES
# ==================================================

elif page == "🔧 Categories":

    st.title("🔧 Home Problem Categories")

    categories = {

        "🚰 Plumbing": [
            "Leaking tap",
            "Slow drainage",
            "Water leakage",
            "Low water flow"
        ],

        "💡 Electrical": [
            "Light not working",
            "Switch problem",
            "Fan problem",
            "Socket problem"
        ],

        "❄️ Appliances": [
            "Refrigerator problem",
            "AC problem",
            "Washing machine problem",
            "Microwave problem"
        ],

        "🚪 Doors & Windows": [
            "Noisy door",
            "Door alignment",
            "Window problem",
            "Hinge problem"
        ],

        "🧹 Cleaning": [
            "Kitchen odor",
            "Bathroom cleaning",
            "Dust problem",
            "General cleaning"
        ]
    }

    for category, problems in categories.items():

        with st.expander(category):

            for problem in problems:

                st.write(
                    "• " + problem
                )


# ==================================================
# KNOWLEDGE BASE
# ==================================================

elif page == "📚 Knowledge Base":

    st.title("📚 HomeFix Knowledge Base")

    st.write(
        "ChromaDB stores the knowledge used by HomeFix AI."
    )

    st.metric(
        "📚 Total Knowledge",
        collection.count()
    )

    st.divider()

    st.subheader("➕ Add Knowledge")

    new_text = st.text_area(
        "Enter useful home information"
    )

    if st.button(
        "➕ Add Knowledge"
    ):

        if new_text.strip() == "":

            st.warning(
                "Please enter some information."
            )

        else:

            new_embedding = model.encode(
                [new_text]
            ).tolist()

            new_id = (
                "custom_"
                + str(datetime.now().timestamp())
            )

            collection.add(
                documents=[new_text],
                embeddings=new_embedding,
                ids=[new_id]
            )

            st.success(
                "✅ Added to ChromaDB"
            )

    st.divider()

    st.subheader("🔎 Search Knowledge")

    search_text = st.text_input(
        "Search HomeFix knowledge"
    )

    if st.button(
        "🔍 Search"
    ):

        if search_text.strip():

            results = search_knowledge(
                search_text
            )

            if results:

                for i, result in enumerate(
                    results
                ):

                    st.info(
                        f"📖 Result {i + 1}\n\n{result}"
                    )

            else:

                st.warning(
                    "No information found."
                )


# ==================================================
# PROBLEM HISTORY
# ==================================================

elif page == "📋 Problem History":

    st.title("📋 Problem History")

    if len(st.session_state.history) == 0:

        st.info(
            "No problems have been checked yet."
        )

    else:

        for item in reversed(
            st.session_state.history
        ):

            with st.expander(
                "🔧 " + item["problem"]
            ):

                st.write(
                    "📂 Category:",
                    item["category"]
                )

                st.write(
                    "🕒 Date:",
                    item["date"]
                )

                st.divider()

                st.markdown(
                    item["answer"]
                )


# ==================================================
# MAINTENANCE
# ==================================================

elif page == "🛠️ Maintenance":

    st.title("🛠️ Home Maintenance Planner")

    st.write(
        "Track your regular home-maintenance tasks."
    )

    for i in range(
        len(st.session_state.maintenance)
    ):

        task = st.session_state.maintenance[i][0]

        checked = st.checkbox(
            task,
            value=st.session_state.maintenance[i][1],
            key="task_" + str(i)
        )

        st.session_state.maintenance[i][1] = checked

    completed = 0

    for item in st.session_state.maintenance:

        if item[1]:
            completed += 1

    total = len(
        st.session_state.maintenance
    )

    st.divider()

    st.write(
        f"✅ {completed} of {total} tasks completed"
    )

    if total > 0:

        st.progress(
            completed / total
        )

    st.divider()

    st.subheader(
        "➕ Add Maintenance Task"
    )

    new_task = st.text_input(
        "Enter task"
    )

    if st.button(
        "Add Task"
    ):

        if new_task.strip():

            st.session_state.maintenance.append(
                [
                    "🔧 " + new_task,
                    False
                ]
            )

            st.success(
                "✅ Task added"
            )


# ==================================================
# SAFETY CENTER
# ==================================================

elif page == "⚠️ Safety Center":

    st.title("⚠️ Home Safety Center")

    st.warning(
        "HomeFix AI provides general information. "
        "It is not a replacement for a qualified professional."
    )

    st.divider()

    st.subheader("💡 Electrical Safety")

    st.write(
        "• Do not touch exposed electrical wires.\n\n"
        "• Do not open electrical equipment if you are not qualified.\n\n"
        "• Stop using damaged electrical equipment.\n\n"
        "• Contact a qualified electrician for electrical faults."
    )

    st.subheader("🔥 Gas Safety")

    st.write(
        "• Do not attempt to repair gas equipment yourself.\n\n"
        "• If you suspect a gas problem, move away from the area.\n\n"
        "• Contact the appropriate qualified service."
    )

    st.subheader("🚰 Water Safety")

    st.write(
        "• Be careful around water near electrical equipment.\n\n"
        "• Contact a qualified professional for major leaks."
    )

    st.subheader("🛠️ General Safety")

    st.write(
        "• Do not attempt dangerous repairs.\n\n"
        "• When unsure, contact a qualified professional.\n\n"
        "• Follow manufacturer instructions for appliances."
    )

    st.success(
        "🏠 Safety first. Fix smart, not risky."
    )