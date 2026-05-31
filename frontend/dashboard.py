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
    * { font-family: 'Inter', sans-serif !important; }

    .stApp { background: #f5f6fa; min-height: 100vh; }
    #MainMenu, footer, header, .stDeployButton { visibility: hidden; }

    .block-container { padding: 2rem 2.5rem !important; max-width: 1100px !important; }

    .welcome-card {
        background: linear-gradient(135deg, #3f51b5, #5c6bc0);
        border-radius: 20px;
        padding: 2rem 2.5rem;
        color: white;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }

    .welcome-card h2 {
        font-size: 1.6rem !important;
        font-weight: 700 !important;
        margin: 0 !important;
        color: white !important;
    }

    .welcome-card p {
        color: rgba(255,255,255,0.8) !important;
        margin: 0.25rem 0 0 0 !important;
        font-size: 0.95rem !important;
    }

    .stat-card {
        background: white;
        border-radius: 16px;
        padding: 1.25rem 1.5rem;
        box-shadow: 0 2px 12px rgba(0,0,0,0.06);
        text-align: center;
        border-left: 4px solid #3f51b5;
    }

    .stat-card .stat-value {
        font-size: 2rem;
        font-weight: 700;
        color: #3f51b5;
    }

    .stat-card .stat-label {
        font-size: 0.8rem;
        color: #757575;
        margin-top: 0.25rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .section-title {
        font-size: 1rem !important;
        font-weight: 600 !important;
        color: #212121 !important;
        margin: 1.5rem 0 0.75rem 0 !important;
    }

    .chat-card {
        background: white;
        border-radius: 14px;
        padding: 1rem 1.25rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        margin-bottom: 0.75rem;
        border-left: 3px solid #e8eaf6;
        cursor: pointer;
        transition: all 0.2s;
    }

    .chat-card:hover {
        border-left-color: #3f51b5;
        box-shadow: 0 4px 16px rgba(63,81,181,0.1);
    }

    .chat-card .chat-title {
        font-weight: 600;
        color: #212121;
        font-size: 0.9rem;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .chat-card .chat-date {
        font-size: 0.75rem;
        color: #9e9e9e;
        margin-top: 0.2rem;
    }

    .stButton > button {
        background: linear-gradient(135deg, #3f51b5, #5c6bc0) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.65rem 1rem !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        width: 100% !important;
        box-shadow: 0 4px 15px rgba(63,81,181,0.25) !important;
        transition: all 0.2s !important;
    }

    .stButton > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 20px rgba(63,81,181,0.35) !important;
    }

    .logout-btn > button {
        background: white !important;
        color: #f44336 !important;
        border: 1.5px solid #f44336 !important;
        box-shadow: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Welcome card
    hour = datetime.now().hour
    greeting = "Good morning" if hour < 12 else "Good afternoon" if hour < 17 else "Good evening"

    st.markdown(f"""
    <div class="welcome-card">
        <div>
            <h2>{greeting}, {user.get('name', 'User')} 👋</h2>
            <p>Welcome back to NIST AI Helpdesk. How can we help you today?</p>
        </div>
        <div style="font-size:4rem;">🎓</div>
    </div>
    """, unsafe_allow_html=True)

    # Stats
    try:
        stats = requests.get(f"{API_URL}/stats").json()
    except:
        stats = {"total_users": 0, "total_tickets": 0, "open_tickets": 0, "resolved_tickets": 0, "total_messages": 0}

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""<div class="stat-card">
            <div class="stat-value">{stats.get('total_messages', 0)}</div>
            <div class="stat-label">Messages</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="stat-card" style="border-left-color:#4caf50;">
            <div class="stat-value" style="color:#4caf50;">{stats.get('resolved_tickets', 0)}</div>
            <div class="stat-label">Resolved</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="stat-card" style="border-left-color:#ff9800;">
            <div class="stat-value" style="color:#ff9800;">{stats.get('open_tickets', 0)}</div>
            <div class="stat-label">Open Tickets</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""<div class="stat-card" style="border-left-color:#9c27b0;">
            <div class="stat-value" style="color:#9c27b0;">{stats.get('total_users', 0)}</div>
            <div class="stat-label">Users</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.markdown("<div class='section-title'>💬 Recent Conversations</div>", unsafe_allow_html=True)
        try:
            sessions = requests.get(f"{API_URL}/sessions/{user['id']}").json()
        except:
            sessions = []

        if not sessions:
            st.markdown("""
            <div style="background:white;border-radius:14px;padding:2rem;text-align:center;
                        box-shadow:0 2px 10px rgba(0,0,0,0.05);color:#9e9e9e;">
                <div style="font-size:2.5rem;">💬</div>
                <div style="margin-top:0.5rem;font-size:0.9rem;">No conversations yet. Start your first chat!</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            for s in sessions[:5]:
                date = s["created_at"][:10] if s.get("created_at") else ""
                st.markdown(f"""
                <div class="chat-card">
                    <div class="chat-title">💬 {s['title']}</div>
                    <div class="chat-date">🕐 {date}</div>
                </div>
                """, unsafe_allow_html=True)
                if st.button("Open", key=f"open_{s['id']}"):
                    st.session_state.screen = "chat"
                    st.session_state.session_id = s["id"]
                    msgs = requests.get(f"{API_URL}/messages/{s['id']}").json()
                    st.session_state.messages = [{"role": m["role"], "content": m["content"]} for m in msgs]
                    st.rerun()

    with col_right:
        st.markdown("<div class='section-title'>🚀 Quick Actions</div>", unsafe_allow_html=True)

        if st.button("➕ Start New Chat"):
            st.session_state.screen = "chat"
            st.session_state.messages = []
            st.session_state.session_id = None
            st.rerun()

        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

        quick = [
            "What is the B.Tech fee?",
            "Tell me about placements",
            "Hostel charges?",
            "How to apply?",
        ]
        for q in quick:
            if st.button(q, key=f"quick_{q}"):
                st.session_state.screen = "chat"
                st.session_state.messages = []
                st.session_state.session_id = None
                st.session_state.quick_question = q
                st.rerun()

        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
        st.markdown("<div class='logout-btn'>", unsafe_allow_html=True)
        if st.button("🚪 Logout"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
