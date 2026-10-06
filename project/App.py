import streamlit as st
import ollama
import json
import uuid
from pathlib import Path
from datetime import datetime
st.set_page_config(page_title="Student Share",page_icon="🎓",layout="wide")
BASE=Path("student_share_data")
FILES=BASE/"files"
RESOURCES=BASE/"resources.json"
DISCUSSIONS=BASE/"discussions.json"
PROFILE=BASE/"profile.json"
STATS=BASE/"stats.json"
FILES.mkdir(parents=True,exist_ok=True)
BASE.mkdir(parents=True,exist_ok=True)
MODEL="llama3.2:3b"
def load_json(path,default):
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except:
            return default
    return default
def save_json(path,data):
    path.write_text(json.dumps(data,indent=2,ensure_ascii=False),encoding="utf-8")
resources=load_json(RESOURCES,[])
discussions=load_json(DISCUSSIONS,[])
profile=load_json(PROFILE,{"name":"","branch":"","year":"","college":""})
stats=load_json(STATS,{"questions":0,"views":0,"useful":0})
if "page" not in st.session_state:
    st.session_state.page="🏠 Home"
if "chat" not in st.session_state:
    st.session_state.chat=[]
if "profile" not in st.session_state:
    st.session_state.profile=profile
if "search" not in st.session_state:
    st.session_state.search=""
def save_all():
    save_json(RESOURCES,resources)
    save_json(DISCUSSIONS,discussions)
    save_json(PROFILE,st.session_state.profile)
    save_json(STATS,stats)
def ai(prompt):
    try:
        result=ollama.chat(model=MODEL,messages=[{"role":"user","content":prompt}])
        return result["message"]["content"]
    except Exception as e:
        return "❌ Ollama error: "+str(e)
def get_file_text(r):
    path=FILES/r["stored_file"]
    if path.exists():
        try:
            return path.read_text(encoding="utf-8")
        except:
            return ""
    return ""
def find_context(text,question):
    words=[w.lower() for w in question.split() if len(w)>2]
    sentences=[]
    for s in text.replace("\n"," ").split("."):
        score=sum(1 for w in words if w in s.lower())
        if score>0:
            sentences.append((score,s.strip()))
    sentences.sort(reverse=True)
    result=[x[1] for x in sentences[:8] if x[1]]
    if not result:
        return text[:5000]
    return ". ".join(result)
def resource_card(r):
    st.markdown(f"### 📘 {r['title']}")
    st.write(f"**Subject:** {r['subject']}  |  **Topic:** {r['topic']}")
    st.write(f"👤 {r['student']}  •  📅 {r['date']}")
    st.write(r["description"])
    c1,c2,c3=st.columns(3)
    with c1:
        st.write(f"⭐ {r['rating']:.1f}/5")
    with c2:
        st.write(f"👁️ {r['views']} views")
    with c3:
        st.write(f"❤️ {r['useful']} useful")
    if r.get("link"):
        st.markdown(f"🔗 {r['link']}")
    path=FILES/r["stored_file"]
    if path.exists():
        with open(path,"rb") as f:
            st.download_button("⬇️ Download",f,file_name=r["file_name"],key="download_"+r["id"])
    c1,c2=st.columns(2)
    with c1:
        rating=st.selectbox("Rating",[1,2,3,4,5],index=4,key="rating_"+r["id"])
        if st.button("⭐ Rate",key="rate_"+r["id"]):
            r["rating"]=(r["rating"]+rating)/2
            save_all()
            st.success("Rating saved!")
            st.rerun()
    with c2:
        if st.button("❤️ Useful",key="useful_"+r["id"]):
            r["useful"]+=1
            stats["useful"]+=1
            save_all()
            st.success("Marked as useful!")
            st.rerun()
    st.divider()
st.sidebar.title("🎓 Student Share")
st.sidebar.caption("Learn • Share • Collaborate • Grow 🚀")
st.sidebar.divider()
menu=["🏠 Home","📚 Explore Resources","📤 Share Material","🔎 Search","🤖 AI Assistant","📝 Ask From Notes","💬 Discussions","⭐ Top Resources","📁 My Resources","📊 Dashboard","👤 Student Profile"]
for item in menu:
    if st.sidebar.button(item,use_container_width=True):
        st.session_state.page=item
        st.rerun()
st.sidebar.divider()
if st.session_state.profile["name"]:
    st.sidebar.success("👋 "+st.session_state.profile["name"])
else:
    st.sidebar.info("👤 Create your profile")
st.sidebar.caption("Powered by Ollama 🤖")
if st.session_state.page=="🏠 Home":
    st.title("🎓 Student Share")
    st.subheader("Learn • Share • Collaborate • Grow 🚀")
    st.write("A student-friendly platform to share study materials, discover useful resources and learn with local AI.")
    st.divider()
    c1,c2,c3,c4=st.columns(4)
    with c1:
        st.metric("📚 Materials",len(resources))
    with c2:
        students=len(set(r["student"] for r in resources if r["student"]))
        st.metric("👨‍🎓 Students",students)
    with c3:
        subjects=len(set(r["subject"] for r in resources))
        st.metric("📖 Subjects",subjects)
    with c4:
        useful=sum(r["useful"] for r in resources)
        st.metric("❤️ Useful",useful)
    st.divider()
    st.subheader("🚀 What can you do?")
    c1,c2,c3,c4=st.columns(4)
    with c1:
        if st.button("📚 Explore Resources",use_container_width=True):
            st.session_state.page="📚 Explore Resources"
            st.rerun()
    with c2:
        if st.button("📤 Share Material",use_container_width=True):
            st.session_state.page="📤 Share Material"
            st.rerun()
    with c3:
        if st.button("🤖 Ask AI",use_container_width=True):
            st.session_state.page="🤖 AI Assistant"
            st.rerun()
    with c4:
        if st.button("💬 Discussions",use_container_width=True):
            st.session_state.page="💬 Discussions"
            st.rerun()
    st.divider()
    st.subheader("💡 Why Student Share?")
    c1,c2,c3=st.columns(3)
    with c1:
        st.info("📚 **Share Knowledge**\n\nStudents can share notes and study materials.")
    with c2:
        st.info("🔎 **Find Resources**\n\nSearch useful materials by subject and topic.")
    with c3:
        st.info("🤖 **Learn with AI**\n\nUse Ollama to understand difficult topics.")
    st.divider()
    st.subheader("🔥 Recent Resources")
    if resources:
        for r in resources[-3:][::-1]:
            st.write(f"📘 **{r['title']}** — {r['subject']} — {r['topic']}")
    else:
        st.info("No resources yet. Be the first student to share!")
elif st.session_state.page=="👤 Student Profile":
    st.title("👤 Student Profile")
    st.write("Create your simple local student profile.")
    with st.form("profile_form"):
        name=st.text_input("👤 Student Name",value=st.session_state.profile["name"])
        branch=st.text_input("🎓 Branch",value=st.session_state.profile["branch"])
        year=st.selectbox("📅 Year",["1st Year","2nd Year","3rd Year","4th Year"],index=["1st Year","2nd Year","3rd Year","4th Year"].index(st.session_state.profile["year"]) if st.session_state.profile["year"] in ["1st Year","2nd Year","3rd Year","4th Year"] else 0)
        college=st.text_input("🏫 College",value=st.session_state.profile["college"])
        submitted=st.form_submit_button("💾 Save Profile",use_container_width=True)
    if submitted:
        st.session_state.profile={"name":name,"branch":branch,"year":year,"college":college}
        save_all()
        st.success("✅ Profile saved successfully!")
    if st.session_state.profile["name"]:
        st.divider()
        st.subheader("✨ Your Profile")
        st.write("👤 **Name:** "+st.session_state.profile["name"])
        st.write("🎓 **Branch:** "+st.session_state.profile["branch"])
        st.write("📅 **Year:** "+st.session_state.profile["year"])
        st.write("🏫 **College:** "+st.session_state.profile["college"])
elif st.session_state.page=="📤 Share Material":
    st.title("📤 Share Study Material")
    st.write("Help another student by sharing your notes.")
    with st.form("upload_form"):
        name=st.text_input("👤 Student Name",value=st.session_state.profile["name"])
        subject=st.selectbox("📚 Subject",["DBMS","Java","Python","Computer Networks","Mathematics","Digital Electronics","Artificial Intelligence","Other"])
        topic=st.text_input("📝 Topic")
        title=st.text_input("📘 Material Title")
        description=st.text_area("📄 Description")
        material_type=st.selectbox("📂 Material Type",["Notes","Question Paper","Assignment","Study Guide","Important Questions","Other"])
        link=st.text_input("🔗 Useful Link (optional)")
        uploaded=st.file_uploader("📎 Upload TXT File",type=["txt"])
        submit=st.form_submit_button("🚀 Share Material",use_container_width=True)
    if submit:
        if not name or not title or not subject or not uploaded:
            st.error("⚠️ Please fill Name, Title, Subject and upload a TXT file.")
        else:
            rid=str(uuid.uuid4())[:8]
            stored=rid+".txt"
            data=uploaded.getvalue()
            (FILES/stored).write_bytes(data)
            r={"id":rid,"student":name,"subject":subject,"topic":topic or "General","title":title,"description":description or "Student shared study material.","material_type":material_type,"link":link,"file_name":uploaded.name,"stored_file":stored,"date":datetime.now().strftime("%d-%m-%Y"),"rating":0.0,"views":0,"useful":0}
            resources.append(r)
            save_all()
            st.success("🎉 Material shared successfully!")
            st.balloons()
elif st.session_state.page=="📚 Explore Resources":
    st.title("📚 Explore Resources")
    st.write("Discover study materials shared by students.")
    if not resources:
        st.info("📭 No resources available yet.")
    else:
        subjects=["All"]+sorted(set(r["subject"] for r in resources))
        selected=st.selectbox("📚 Filter by Subject",subjects)
        filtered=resources if selected=="All" else [r for r in resources if r["subject"]==selected]
        st.write(f"Showing **{len(filtered)}** resources")
        for r in filtered[::-1]:
            resource_card(r)
elif st.session_state.page=="🔎 Search":
    st.title("🔎 Search Resources")
    query=st.text_input("Search by subject, topic, title or keywords",value=st.session_state.search)
    st.session_state.search=query
    if query:
        words=query.lower().split()
        results=[]
        for r in resources:
            text=(r["title"]+" "+r["subject"]+" "+r["topic"]+" "+r["description"]).lower()
            score=sum(1 for w in words if w in text)
            if score>0:
                results.append((score,r))
        results.sort(key=lambda x:(x[0],x[1]["rating"],x[1]["useful"]),reverse=True)
        if results:
            st.success(f"🔍 Found {len(results)} resources")
            for score,r in results:
                st.caption(f"Match score: {score}")
                resource_card(r)
        else:
            st.warning("No matching resources found.")
    else:
        st.info("💡 Try searching: DBMS transactions, Java inheritance, Python loops...")
elif st.session_state.page=="🤖 AI Assistant":
    st.title("🤖 AI Study Assistant")
    st.write("Ask Ollama anything about your studies.")
    if st.session_state.chat:
        for m in st.session_state.chat:
            with st.chat_message(m["role"]):
                st.write(m["content"])
    question=st.chat_input("Ask your study question...")
    if question:
        st.session_state.chat.append({"role":"user","content":question})
        answer=ai("You are a friendly college study assistant. Explain the answer in very simple English with short points and examples. Student question: "+question)
        st.session_state.chat.append({"role":"assistant","content":answer})
        st.rerun()
    if st.button("🗑️ Clear Chat"):
        st.session_state.chat=[]
        st.rerun()
elif st.session_state.page=="📝 Ask From Notes":
    st.title("📝 Ask From Your Notes")
    st.write("Select an uploaded TXT resource and ask a question.")
    if not resources:
        st.info("📭 Upload a TXT study material first.")
    else:
        selected_id=st.selectbox("📘 Select Material",resources,format_func=lambda r:r["title"])
        question=st.text_area("❓ Your Question")
        if st.button("🤖 Ask From Notes",use_container_width=True):
            if not question:
                st.warning("Please enter a question.")
            else:
                text=get_file_text(selected_id)
                context=find_context(text,question)
                prompt=f"""You are a college study assistant.
Answer the student's question using the notes below.
If the notes do not contain the answer, clearly say that the answer is not available in the selected notes.
Use simple English.
NOTES:
{context}
QUESTION:
{question}"""
                answer=ai(prompt)
                stats["questions"]+=1
                selected_id["views"]+=1
                stats["views"]+=1
                save_all()
                st.subheader("🤖 AI Answer")
                st.write(answer)
                st.success("📚 Answer generated using the selected notes.")
                with st.expander("📖 Source Context"):
                    st.write(context)
elif st.session_state.page=="💬 Discussions":
    st.title("💬 Student Discussions")
    st.write("Ask questions and share knowledge with other students.")
    with st.form("discussion_form"):
        student=st.text_input("👤 Your Name",value=st.session_state.profile["name"])
        question=st.text_area("❓ Ask a Question")
        subject=st.selectbox("📚 Subject",["DBMS","Java","Python","Computer Networks","Mathematics","Digital Electronics","AI","General"])
        post=st.form_submit_button("📢 Post Question",use_container_width=True)
    if post:
        if student and question:
            discussions.append({"id":str(uuid.uuid4())[:8],"student":student,"question":question,"subject":subject,"date":datetime.now().strftime("%d-%m-%Y"),"answers":[],"likes":0})
            save_all()
            st.success("✅ Question posted!")
            st.rerun()
        else:
            st.warning("Please enter your name and question.")
    st.divider()
    if not discussions:
        st.info("No discussions yet. Start the first discussion!")
    for d in discussions[::-1]:
        st.subheader("❓ "+d["question"])
        st.caption(f"👤 {d['student']}  •  📚 {d['subject']}  •  📅 {d['date']}")
        if d["answers"]:
            st.write("💬 **Answers:**")
            for a in d["answers"]:
                st.write("➡️ "+a)
        with st.form("answer_"+d["id"]):
            answer=st.text_input("Write an answer",key="ans_"+d["id"])
            send=st.form_submit_button("💬 Answer")
        if send and answer:
            d["answers"].append(answer)
            save_all()
            st.rerun()
        if st.button("👍 Like",key="like_"+d["id"]):
            d["likes"]+=1
            save_all()
            st.rerun()
        st.write(f"👍 {d['likes']} likes")
        st.divider()
elif st.session_state.page=="⭐ Top Resources":
    st.title("⭐ Top Resources")
    st.write("Most useful and highly rated study materials.")
    if resources:
        top=sorted(resources,key=lambda r:(r["rating"],r["useful"],r["views"]),reverse=True)
        for i,r in enumerate(top[:10],1):
            st.subheader(f"#{i} 🏆 {r['title']}")
            resource_card(r)
    else:
        st.info("No resources available.")
elif st.session_state.page=="📁 My Resources":
    st.title("📁 My Resources")
    name=st.session_state.profile["name"]
    if not name:
        st.warning("Please create your profile first.")
    else:
        mine=[r for r in resources if r["student"].lower()==name.lower()]
        st.metric("📚 Materials Shared",len(mine))
        if mine:
            for r in mine[::-1]:
                resource_card(r)
        else:
            st.info("You have not shared any resources yet.")
elif st.session_state.page=="📊 Dashboard":
    st.title("📊 Student Dashboard")
    name=st.session_state.profile["name"]
    mine=[r for r in resources if name and r["student"].lower()==name.lower()]
    total_views=sum(r["views"] for r in mine)
    total_useful=sum(r["useful"] for r in mine)
    c1,c2,c3,c4=st.columns(4)
    with c1:
        st.metric("📚 Shared",len(mine))
    with c2:
        st.metric("👁️ Views",total_views)
    with c3:
        st.metric("❤️ Useful",total_useful)
    with c4:
        st.metric("❓ Questions",stats["questions"])
    st.divider()
    st.subheader("📈 Your Activity")
    if mine:
        for r in mine:
            st.write(f"📘 {r['title']} — 👁️ {r['views']} views — ❤️ {r['useful']} useful")
    else:
        st.info("Share your first study material to see activity here.")
    st.divider()
    st.subheader("🌟 Platform Statistics")
    c1,c2,c3=st.columns(3)
    with c1:
        st.metric("📚 Total Materials",len(resources))
    with c2:
        st.metric("💬 Discussions",len(discussions))
    with c3:
        st.metric("🤖 Questions Asked",stats["questions"])
st.divider()
st.caption("🎓 Student Share • Built for students • Local AI with Ollama 🤖")