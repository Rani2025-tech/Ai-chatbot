import streamlit as st
import requests
import json

st.set_page_config(page_title="AI Chat — NIST Helpdesk", page_icon="🤖", layout="wide")

API_URL = "http://localhost:8000/api"

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap');
* { font-family: 'Poppins', sans-serif !important; box-sizing: border-box; }

.stApp {
    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    min-height: 100vh;
}
.block-container { padding: 2rem 3rem !important; max-width: 1400px !important; }

.nist-header {
    background: linear-gradient(135deg, rgba(255,255,255,0.08), rgba(255,255,255,0.03));
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 24px;
    padding: 2.5rem 3rem;
    margin-bottom: 2rem;
    text-align: center;
    backdrop-filter: blur(20px);
    position: relative;
    overflow: hidden;
}
.nist-header h1 {
    font-size: 3rem !important; font-weight: 800 !important;
    background: linear-gradient(135deg, #667eea, #764ba2, #f093fb);
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
    margin: 0 !important;
}
.nist-header .subtitle { color: rgba(255,255,255,0.6); font-size: 1.1rem; margin-top: 0.75rem; }
.nist-header .badge {
    display: inline-block;
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white; padding: 0.3rem 1rem; border-radius: 50px;
    font-size: 0.8rem; font-weight: 600; margin-top: 1rem;
    letter-spacing: 1px; text-transform: uppercase;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(15,12,41,0.95), rgba(48,43,99,0.95)) !important;
    border-right: 1px solid rgba(255,255,255,0.08) !important;
}
section[data-testid="stSidebar"] .block-container { padding: 2rem 1.5rem !important; }

.sidebar-logo { text-align: center; padding: 1.5rem 0; border-bottom: 1px solid rgba(255,255,255,0.08); margin-bottom: 1.5rem; }
.sidebar-logo h2 { color: white !important; font-size: 1.4rem !important; font-weight: 700 !important; margin: 0.5rem 0 0 0 !important; }
.sidebar-logo p { color: rgba(255,255,255,0.4) !important; font-size: 0.75rem !important; margin: 0.25rem 0 0 0 !important; }

.sidebar-card { background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.08); border-radius: 16px; padding: 1.5rem; margin-bottom: 1.25rem; }
.sidebar-card-title { color: rgba(255,255,255,0.9) !important; font-size: 0.9rem !important; font-weight: 600 !important; text-transform: uppercase !important; letter-spacing: 1px !important; margin-bottom: 1rem !important; }

.doc-badge { background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 0.2rem 0.75rem; border-radius: 50px; font-size: 0.75rem; font-weight: 600; display: inline-block; margin-bottom: 0.75rem; }
.doc-item { background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.06); border-left: 3px solid #667eea; border-radius: 8px; padding: 0.6rem 0.9rem; margin-bottom: 0.5rem; color: rgba(255,255,255,0.7) !important; font-size: 0.8rem !important; }

.chat-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.5rem; padding-bottom: 1rem; border-bottom: 1px solid rgba(255,255,255,0.08); }
.chat-title { color: white !important; font-size: 1.1rem !important; font-weight: 600 !important; margin: 0 !important; }
.online-badge { background: rgba(72,187,120,0.15); border: 1px solid rgba(72,187,120,0.3); color: #48bb78; padding: 0.3rem 0.9rem; border-radius: 50px; font-size: 0.75rem; font-weight: 600; display: flex; align-items: center; gap: 0.4rem; }
.online-dot { width: 8px; height: 8px; background: #48bb78; border-radius: 50%; animation: blink 1.5s infinite; display: inline-block; }
@keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0.3; } }

.stChatMessage { background: rgba(255,255,255,0.04) !important; border: 1px solid rgba(255,255,255,0.08) !important; border-radius: 20px !important; padding: 1.25rem 1.25rem 1.25rem 4rem !important; margin-bottom: 1rem !important; backdrop-filter: blur(10px) !important; position: relative !important; }
.stChatMessage p, .stChatMessage li, .stChatMessage div { color: rgba(255,255,255,0.9) !important; font-size: 0.95rem !important; line-height: 1.7 !important; }

.stButton > button { background: linear-gradient(135deg, #667eea, #764ba2) !important; color: white !important; border: none !important; border-radius: 12px !important; padding: 0.7rem 1.8rem !important; font-weight: 600 !important; font-size: 0.9rem !important; transition: all 0.3s ease !important; box-shadow: 0 4px 20px rgba(102,126,234,0.35) !important; width: 100% !important; }

.stFileUploader { background: rgba(255,255,255,0.03) !important; border: 2px dashed rgba(102,126,234,0.4) !important; border-radius: 12px !important; padding: 1rem !important; }
.stFileUploader label { color: rgba(255,255,255,0.6) !important; }

.stSelectbox label { color: rgba(255,255,255,0.7) !important; font-size: 0.85rem !important; font-weight: 500 !important; }
.stSelectbox > div > div { background: rgba(255,255,255,0.06) !important; border: 1px solid rgba(255,255,255,0.12) !important; border-radius: 10px !important; color: white !important; }

.stChatInput > div { background: rgba(255,255,255,0.06) !important; border: 1px solid rgba(255,255,255,0.12) !important; border-radius: 16px !important; }
.stChatInput textarea { color: white !important; font-size: 0.95rem !important; }
.stChatInput textarea::placeholder { color: rgba(255,255,255,0.35) !important; }

.stSuccess { background: rgba(72,187,120,0.12) !important; border: 1px solid rgba(72,187,120,0.3) !important; border-radius: 12px !important; color: #9ae6b4 !important; }
.stError { background: rgba(245,101,101,0.12) !important; border: 1px solid rgba(245,101,101,0.3) !important; border-radius: 12px !important; color: #feb2b2 !important; }
.stInfo { background: rgba(66,153,225,0.12) !important; border: 1px solid rgba(66,153,225,0.3) !important; border-radius: 12px !important; color: #bee3f8 !important; }
.stWarning { background: rgba(237,137,54,0.12) !important; border: 1px solid rgba(237,137,54,0.3) !important; border-radius: 12px !important; color: #fbd38d !important; }

::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-thumb { background: rgba(102,126,234,0.4); border-radius: 3px; }

#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ──────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sidebar-logo">
        <div style="font-size: 3rem;">🎓</div>
        <h2>NIST Helpdesk</h2>
        <p>AI-Powered Assistant</p>
    </div>
    """, unsafe_allow_html=True)

    # Upload section
    st.markdown('<div class="sidebar-card">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-card-title">📄 Upload Document</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("", type="pdf", label_visibility="collapsed")
    if uploaded_file is not None:
        if st.button("🚀 Process Document"):
            with st.spinner("Processing..."):
                try:
                    files = {"file": (uploaded_file.name, uploaded_file, "application/pdf")}
                    response = requests.post(f"{API_URL}/upload", files=files)
                    if response.status_code == 200:
                        data = response.json()
                        st.success("✅ Uploaded successfully!")
                        st.info(f"📦 {data['chunks_created']} chunks indexed")
                    else:
                        st.error(f"❌ {response.json()['detail']}")
                except Exception as e:
                    st.error(f"❌ Server error: {str(e)}")
    st.markdown('</div>', unsafe_allow_html=True)

    # Knowledge base
    st.markdown('<div class="sidebar-card">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-card-title">📚 Knowledge Base</div>', unsafe_allow_html=True)
    try:
        response = requests.get(f"{API_URL}/documents")
        if response.status_code == 200:
            data = response.json()
            if data["total"] == 0:
                st.markdown('<p style="color:rgba(255,255,255,0.4);font-size:0.85rem;">No documents loaded yet.</p>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="doc-badge">📊 {data["total"]} Documents</div>', unsafe_allow_html=True)
                with st.expander("View all documents"):
                    for doc in data["documents"]:
                        st.markdown(f'<div class="doc-item">📄 {doc}</div>', unsafe_allow_html=True)
    except:
        st.warning("⚠️ Server not reachable")
    st.markdown('</div>', unsafe_allow_html=True)

    # Quick questions
    st.markdown('<div class="sidebar-card">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-card-title">⚡ Quick Questions</div>', unsafe_allow_html=True)
    for q in ["What is the B.Tech fee?", "Tell me about placements", "What are the hostel charges?", "How to apply for admission?", "What courses are offered?"]:
        if st.button(q, key=f"qq_{q}"):
            st.session_state.quick_question = q
    st.markdown('</div>', unsafe_allow_html=True)

# ── Main Content ─────────────────────────────────────────────────
st.markdown("""
<div class="nist-header">
    <h1>🎓 NIST AI Helpdesk</h1>
    <div class="subtitle">National Institute of Science & Technology, Berhampur, Odisha</div>
    <div class="badge">✨ Powered by RAG + Llama 3.2</div>
</div>
""", unsafe_allow_html=True)

# Stats
col1, col2, col3, col4 = st.columns(4)
for col, icon, val, label in zip(
    [col1, col2, col3, col4],
    ["📚", "🌐", "🤖", "⚡"],
    ["7+", "3", "RAG", "100%"],
    ["Documents", "Languages", "AI Engine", "Offline"]
):
    with col:
        st.markdown(f"""
        <div style="background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.08);border-radius:16px;padding:1.25rem;text-align:center;">
            <div style="font-size:2rem;">{icon}</div>
            <div style="color:white;font-size:1.5rem;font-weight:700;">{val}</div>
            <div style="color:rgba(255,255,255,0.5);font-size:0.8rem;">{label}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Language selector
col_lang, col_spacer = st.columns([1, 3])
with col_lang:
    language = st.selectbox(
        "🌐 Response Language",
        options=["auto", "en", "hi", "or"],
        format_func=lambda x: {"auto": "🌐 Auto-detect", "en": "🇬🇧 English", "hi": "🇮🇳 Hindi", "or": "🏛️ Odia"}[x],
        key="lang_select"
    )

# Chat header
st.markdown("""
<div class="chat-header">
    <div class="chat-title">💬 Chat with AI Assistant</div>
    <div class="online-badge"><span class="online-dot"></span> Online</div>
</div>
""", unsafe_allow_html=True)

# Chat
if "messages" not in st.session_state:
    st.session_state.messages = []

if len(st.session_state.messages) == 0:
    with st.chat_message("assistant", avatar="🤖"):
        st.markdown("""
👋 **Welcome to NIST AI Helpdesk!**

I'm your intelligent assistant for **National Institute of Science & Technology, Berhampur**.

Ask me anything about:
- 🎓 **Admissions** — eligibility, process, quotas
- 💰 **Fees** — tuition, hostel, mess charges
- 🏢 **Placements** — companies, packages, stats
- 🏫 **Campus** — labs, sports, facilities
- 📖 **Courses** — B.Tech, MBA, MCA programs
- 🏆 **Scholarships** — merit, government schemes

*Type your question below in English, Hindi, or Odia!*
        """)

for message in st.session_state.messages:
    avatar = "🤖" if message["role"] == "assistant" else "👤"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

prompt = st.chat_input("Ask anything about NIST University...")
if not prompt and st.session_state.get("quick_question"):
    prompt = st.session_state.pop("quick_question")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🤖"):
        message_placeholder = st.empty()
        full_response = ""
        try:
            response = requests.post(f"{API_URL}/ask", json={"question": prompt, "language": language}, stream=True)
            if response.status_code == 200:
                for line in response.iter_lines():
                    if line:
                        line = line.decode('utf-8')
                        if line.startswith('data: '):
                            try:
                                data = json.loads(line[6:])
                                if 'chunk' in data:
                                    full_response += data['chunk']
                                    message_placeholder.markdown(full_response + "▌")
                                elif data.get('done'):
                                    message_placeholder.markdown(full_response)
                                    break
                            except json.JSONDecodeError:
                                continue
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            elif response.status_code == 400:
                st.warning(f"⚠️ {response.json()['detail']}")
            else:
                st.error("❌ Something went wrong. Please try again.")
        except Exception as e:
            st.error(f"❌ Could not connect to server: {str(e)}")
