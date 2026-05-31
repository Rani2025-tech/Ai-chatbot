import streamlit as st
import requests
import os
from datetime import datetime

API_URL = os.getenv("API_URL", "http://localhost:8000/api")

def show():
    user = st.session_state.get("user", {})

    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    * { font-family: 'Inter', sans-serif !important; box-sizing: border-box; }

    .stApp { background: #eef0f8; }
    #MainMenu, footer, header, .stDeployButton { visibility: hidden; }
    .block-container { padding: 1rem 1.5rem !important; max-width: 100% !important; }

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a237e 0%, #283593 100%) !important;
        border-right: none !important;
        box-shadow: 4px 0 20px rgba(0,0,0,0.15) !important;
    }
    section[data-testid="stSidebar"] .block-container { padding: 1.25rem 1rem !important; }
    section[data-testid="stSidebar"] * { color: white !important; }

    .sidebar-header {
        text-align: center;
        padding: 1rem 0 1.25rem 0;
        border-bottom: 1px solid rgba(255,255,255,0.1);
        margin-bottom: 1.25rem;
    }
    .sidebar-logo-icon {
        width: 52px; height: 52px;
        background: rgba(255,255,255,0.12);
        border-radius: 14px;
        display: flex; align-items: center; justify-content: center;
        font-size: 1.6rem;
        margin: 0 auto 0.6rem auto;
        border: 1px solid rgba(255,255,255,0.15);
    }
    .sidebar-header h3 {
        font-size: 1rem !important; font-weight: 700 !important;
        margin: 0 !important; letter-spacing: 0.3px;
    }
    .sidebar-header p {
        font-size: 0.72rem !important; opacity: 0.5 !important;
        margin: 0.2rem 0 0 0 !important;
    }

    .sidebar-section-label {
        font-size: 0.68rem;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        opacity: 0.4;
        margin: 1rem 0 0.5rem 0;
        padding-left: 0.25rem;
    }

    .chat-history-item {
        background: rgba(255,255,255,0.06);
        border-radius: 10px;
        padding: 0.55rem 0.75rem;
        margin-bottom: 0.3rem;
        border-left: 3px solid transparent;
        transition: all 0.2s;
    }
    .chat-history-item:hover {
        background: rgba(255,255,255,0.12);
        border-left-color: #7986cb;
    }
    .chat-history-item .chi-title {
        font-size: 0.8rem; font-weight: 500;
        white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
    }
    .chat-history-item .chi-date {
        font-size: 0.68rem; opacity: 0.45; margin-top: 0.1rem;
    }

    .user-footer {
        margin-top: 1.5rem;
        padding-top: 1rem;
        border-top: 1px solid rgba(255,255,255,0.1);
    }
    .user-avatar {
        width: 34px; height: 34px;
        background: linear-gradient(135deg, #5c6bc0, #7986cb);
        border-radius: 50%;
        display: inline-flex; align-items: center; justify-content: center;
        font-size: 0.85rem; font-weight: 700;
        margin-right: 0.5rem; vertical-align: middle;
    }
    .user-name { font-size: 0.85rem; font-weight: 600; vertical-align: middle; }
    .user-role { font-size: 0.7rem; opacity: 0.5; margin-top: 0.1rem; }

    /* ── Buttons ── */
    .stButton > button {
        background: linear-gradient(135deg, #3f51b5, #5c6bc0) !important;
        color: white !important; border: none !important;
        border-radius: 10px !important; padding: 0.55rem 1rem !important;
        font-weight: 600 !important; font-size: 0.82rem !important;
        width: 100% !important; transition: all 0.2s !important;
        box-shadow: 0 3px 10px rgba(63,81,181,0.3) !important;
        letter-spacing: 0.2px !important;
    }
    .stButton > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 5px 16px rgba(63,81,181,0.45) !important;
    }
    .outline-btn > button {
        background: rgba(255,255,255,0.08) !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        box-shadow: none !important;
    }
    .danger-btn > button {
        background: rgba(244,67,54,0.1) !important;
        border: 1px solid rgba(244,67,54,0.35) !important;
        color: #ef9a9a !important; box-shadow: none !important;
    }
    .feedback-btn > button {
        background: #f5f6fa !important; color: #616161 !important;
        border: 1px solid #e0e0e0 !important; box-shadow: none !important;
        padding: 0.3rem 0.6rem !important; font-size: 0.8rem !important;
        border-radius: 8px !important; width: auto !important;
    }
    .feedback-btn > button:hover {
        background: #e8eaf6 !important; color: #3f51b5 !important;
        border-color: #9fa8da !important; transform: none !important;
    }
    .ticket-btn > button {
        background: #fff8e1 !important; color: #f57f17 !important;
        border: 1px solid #ffe082 !important; box-shadow: none !important;
        padding: 0.3rem 0.75rem !important; font-size: 0.8rem !important;
        border-radius: 8px !important; width: auto !important;
    }

    /* ── Chat topbar ── */
    .chat-topbar {
        background: white;
        border-radius: 16px;
        padding: 0.9rem 1.5rem;
        margin-bottom: 1.25rem;
        display: flex; align-items: center; justify-content: space-between;
        box-shadow: 0 2px 12px rgba(0,0,0,0.06);
        border-bottom: 3px solid #e8eaf6;
    }
    .chat-topbar-left { display: flex; align-items: center; gap: 0.75rem; }
    .bot-avatar-top {
        width: 40px; height: 40px;
        background: linear-gradient(135deg, #3f51b5, #7986cb);
        border-radius: 12px;
        display: flex; align-items: center; justify-content: center;
        font-size: 1.2rem;
    }
    .chat-topbar h4 {
        margin: 0 !important; font-size: 0.95rem !important;
        font-weight: 700 !important; color: #1a237e !important;
    }
    .chat-topbar-sub { font-size: 0.75rem; color: #9e9e9e; margin-top: 0.1rem; }
    .online-pill {
        background: #e8f5e9; color: #2e7d32;
        padding: 0.3rem 0.8rem; border-radius: 20px;
        font-size: 0.75rem; font-weight: 600;
        display: flex; align-items: center; gap: 0.35rem;
        border: 1px solid #c8e6c9;
    }
    .online-dot {
        width: 7px; height: 7px; background: #4caf50;
        border-radius: 50%; animation: blink 1.5s infinite;
    }
    @keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.3} }

    /* ── Chat window ── */
    .chat-window {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        min-height: 420px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
    }

    /* ── Message bubbles ── */
    .msg-row { display: flex; margin-bottom: 1.25rem; align-items: flex-end; gap: 0.5rem; }
    .msg-row.user { flex-direction: row-reverse; }

    .msg-avatar {
        width: 30px; height: 30px; border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        font-size: 0.85rem; flex-shrink: 0;
    }
    .msg-avatar.bot { background: linear-gradient(135deg, #3f51b5, #7986cb); }
    .msg-avatar.user-av { background: linear-gradient(135deg, #26a69a, #4db6ac); color: white; font-weight: 700; }

    .msg-content { display: flex; flex-direction: column; max-width: 68%; }
    .msg-row.user .msg-content { align-items: flex-end; }

    .bubble {
        padding: 0.75rem 1.1rem;
        border-radius: 18px;
        font-size: 0.88rem;
        line-height: 1.6;
        word-wrap: break-word;
    }
    .bubble.bot {
        background: #f8f9ff;
        color: #212121;
        border-radius: 4px 18px 18px 18px;
        border: 1px solid #e8eaf6;
        box-shadow: 0 1px 4px rgba(63,81,181,0.08);
    }
    .bubble.user {
        background: linear-gradient(135deg, #3f51b5, #5c6bc0);
        color: white;
        border-radius: 18px 18px 4px 18px;
        box-shadow: 0 2px 10px rgba(63,81,181,0.3);
    }
    .msg-time {
        font-size: 0.67rem; color: #bdbdbd;
        margin-top: 0.3rem; padding: 0 0.25rem;
    }

    /* ── Typing indicator ── */
    .typing-wrap { display: flex; align-items: flex-end; gap: 0.5rem; margin-bottom: 1rem; }
    .typing-bubble {
        background: #f8f9ff; border: 1px solid #e8eaf6;
        border-radius: 4px 18px 18px 18px;
        padding: 0.75rem 1.1rem;
        display: flex; align-items: center; gap: 0.3rem;
        box-shadow: 0 1px 4px rgba(63,81,181,0.08);
    }
    .typing-dot {
        width: 7px; height: 7px; background: #9fa8da;
        border-radius: 50%; animation: tdot 1.2s infinite;
    }
    .typing-dot:nth-child(2) { animation-delay: 0.2s; }
    .typing-dot:nth-child(3) { animation-delay: 0.4s; }
    @keyframes tdot { 0%,60%,100%{transform:translateY(0);opacity:0.5} 30%{transform:translateY(-5px);opacity:1} }

    /* ── Chat input ── */
    .stChatInput > div {
        background: white !important;
        border: 2px solid #e8eaf6 !important;
        border-radius: 14px !important;
        box-shadow: 0 2px 12px rgba(63,81,181,0.08) !important;
        transition: border-color 0.2s !important;
    }
    .stChatInput > div:focus-within {
        border-color: #7986cb !important;
        box-shadow: 0 2px 16px rgba(63,81,181,0.15) !important;
    }
    .stChatInput textarea { color: #212121 !important; font-size: 0.92rem !important; }
    .stChatInput textarea::placeholder { color: #bdbdbd !important; }

    /* ── Selectbox in sidebar ── */
    .stSelectbox label { color: rgba(255,255,255,0.6) !important; font-size: 0.75rem !important; }
    .stSelectbox > div > div {
        background: rgba(255,255,255,0.08) !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        border-radius: 8px !important; color: white !important;
    }

    /* ── Ticket box ── */
    .ticket-box {
        background: linear-gradient(135deg, #fff8e1, #fffde7);
        border: 1.5px solid #ffe082;
        border-radius: 12px; padding: 1rem 1.25rem;
        margin-top: 0.75rem; font-size: 0.85rem; color: #5d4037;
        box-shadow: 0 2px 8px rgba(255,193,7,0.15);
    }
    .ticket-box code {
        background: rgba(0,0,0,0.06); padding: 0.15rem 0.4rem;
        border-radius: 4px; font-size: 0.82rem;
    }
    </style>
    """, unsafe_allow_html=True)

    # ── Sidebar ──────────────────────────────────────────────────
    with st.sidebar:
        st.markdown(f"""
        <div class="sidebar-header">
            <div class="sidebar-logo-icon">🎓</div>
            <h3>NIST Helpdesk</h3>
            <p>AI-powered support</p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("➕ New Chat", key="new_chat"):
            st.session_state.messages = []
            st.session_state.session_id = None
            st.rerun()

        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

        # Language selector
        language = st.selectbox(
            "🌐 Language",
            options=["auto", "en", "hi", "or"],
            format_func=lambda x: {"auto": "🌐 Auto", "en": "🇬🇧 English", "hi": "🇮🇳 Hindi", "or": "🏛️ Odia"}[x],
            key="lang_select"
        )

        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
        st.markdown("<div class='sidebar-section-label'>Recent Chats</div>", unsafe_allow_html=True)

        # Chat history
        if user.get("id") and user["id"] != "guest":
            try:
                sessions = requests.get(f"{API_URL}/sessions/{user['id']}").json()
                for s in sessions[:8]:
                    date = s["created_at"][:10] if s.get("created_at") else ""
                    st.markdown(f"""
                    <div class="chat-history-item">
                        <div class="chi-title">💬 {s['title']}</div>
                        <div class="chi-date">{date}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button("↩", key=f"load_{s['id']}"):
                        st.session_state.session_id = s["id"]
                        msgs = requests.get(f"{API_URL}/messages/{s['id']}").json()
                        st.session_state.messages = [{"role": m["role"], "content": m["content"]} for m in msgs]
                        st.rerun()
            except:
                pass
        else:
            st.markdown("<div style='font-size:0.8rem;opacity:0.4;'>Login to save history</div>", unsafe_allow_html=True)

        st.markdown("<div class='user-footer'>", unsafe_allow_html=True)
        initial = user.get('name', 'G')[0].upper()
        st.markdown(f"""
        <div style='display:flex;align-items:center;margin-bottom:0.75rem;'>
            <div class='user-avatar'>{initial}</div>
            <div>
                <div class='user-name'>{user.get('name','Guest')}</div>
                <div class='user-role'>{user.get('role','guest').capitalize()}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if user.get("role") != "guest":
            st.markdown("<div class='outline-btn'>", unsafe_allow_html=True)
            if st.button("🏠 Dashboard", key="go_dashboard"):
                st.session_state.screen = "dashboard"
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='danger-btn'>", unsafe_allow_html=True)
        if st.button("🚪 Logout", key="chat_logout"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Main Chat Area ────────────────────────────────────────────
    st.markdown(f"""
    <div class="chat-topbar">
        <div class="chat-topbar-left">
            <div class="bot-avatar-top">🤖</div>
            <div>
                <h4>NIST Bot</h4>
                <div class="chat-topbar-sub">Ask anything about NIST University</div>
            </div>
        </div>
        <div class="online-pill">
            <span class="online-dot"></span> Online
        </div>
    </div>
    """, unsafe_allow_html=True)

    if "messages" not in st.session_state:
        st.session_state.messages = []

    st.markdown('<div class="chat-window">', unsafe_allow_html=True)
    # Welcome message
    if not st.session_state.messages:
        st.markdown("""
        <div class="msg-row">
            <div class="msg-avatar bot">🤖</div>
            <div class="msg-content">
                <div class="bubble bot">
                    👋 <b>Hello! I'm NIST Bot.</b><br><br>
                    I can help you with admissions, fees, hostel, placements, courses and more.<br><br>
                    What would you like to know?
                </div>
                <div class="msg-time">Just now</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Display messages
    now = datetime.now().strftime("%I:%M %p")
    for i, msg in enumerate(st.session_state.messages):
        if msg["role"] == "user":
            initial = user.get('name', 'U')[0].upper()
            st.markdown(f"""
            <div class="msg-row user">
                <div class="msg-avatar user-av">{initial}</div>
                <div class="msg-content">
                    <div class="bubble user">{msg['content']}</div>
                    <div class="msg-time">{now}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="msg-row">
                <div class="msg-avatar bot">🤖</div>
                <div class="msg-content">
                    <div class="bubble bot">{msg['content']}</div>
                    <div class="msg-time">{now}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            col_up, col_down, col_ticket, _ = st.columns([1, 1, 2, 6])
            with col_up:
                st.markdown("<div class='feedback-btn'>", unsafe_allow_html=True)
                st.button("👍", key=f"up_{i}")
                st.markdown("</div>", unsafe_allow_html=True)
            with col_down:
                st.markdown("<div class='feedback-btn'>", unsafe_allow_html=True)
                st.button("👎", key=f"down_{i}")
                st.markdown("</div>", unsafe_allow_html=True)
            with col_ticket:
                st.markdown("<div class='ticket-btn'>", unsafe_allow_html=True)
                if st.button("🎫 Raise Ticket", key=f"ticket_{i}"):
                    if user.get("id") and user["id"] != "guest" and st.session_state.get("session_id"):
                        try:
                            res = requests.post(f"{API_URL}/tickets", json={
                                "user_id": user["id"],
                                "user_name": user["name"],
                                "session_id": st.session_state.session_id,
                                "issue": msg["content"][:200]
                            })
                            tid = res.json().get("ticket_id", "")
                            st.session_state.last_ticket = tid
                        except:
                            pass
                st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.get("last_ticket"):
        st.markdown(f"""
        <div class="ticket-box">
            🎫 <b>Ticket raised successfully!</b><br>
            Ticket ID: <code>{st.session_state.last_ticket}</code><br>
            Our team will get back to you soon.
        </div>
        """, unsafe_allow_html=True)

    # Handle quick question
    prompt = st.chat_input("Type your message...")
    if not prompt and st.session_state.get("quick_question"):
        prompt = st.session_state.pop("quick_question")

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Create session if needed
        if user.get("id") and user["id"] != "guest" and not st.session_state.get("session_id"):
            try:
                res = requests.post(f"{API_URL}/sessions", json={"user_id": user["id"], "title": prompt[:50]})
                st.session_state.session_id = res.json().get("session_id")
            except:
                pass

        with st.spinner(""):
            st.markdown("""
            <div class="typing-wrap">
                <div class="msg-avatar bot">🤖</div>
                <div class="typing-bubble">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            try:
                res = requests.post(f"{API_URL}/ask-sync", json={
                    "question": prompt,
                    "language": st.session_state.get("lang_select", "auto"),
                    "session_id": st.session_state.get("session_id"),
                    "user_id": user.get("id")
                }, timeout=60)

                if res.status_code == 200:
                    answer = res.json()["answer"]
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                elif res.status_code == 400:
                    st.session_state.messages.append({"role": "assistant", "content": f"⚠️ {res.json()['detail']}"})
                else:
                    st.session_state.messages.append({"role": "assistant", "content": "❌ Something went wrong. Please try again."})
            except Exception as e:
                st.session_state.messages.append({"role": "assistant", "content": f"❌ Cannot connect to server: {str(e)}"})

        st.rerun()
