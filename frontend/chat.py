# -*- coding: utf-8 -*-
import html
import logging
from datetime import datetime
import requests
import streamlit as st
import os

logger = logging.getLogger(__name__)
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000/api")
REQUEST_TIMEOUT = 120

LANGUAGE_OPTIONS = {
    "auto": "Auto-detect",
    "en": "English",
    "hi": "Hindi",
    "or": "Odia",
}

def safe(text: str) -> str:
    return html.escape(str(text))

def fmt_time(iso):
    if not iso:
        return ""
    try:
        return datetime.fromisoformat(iso).strftime("%I:%M %p")
    except:
        return ""

def relative_date(iso):
    if not iso:
        return ""
    try:
        dt = datetime.fromisoformat(iso).date()
        today = datetime.now().date()
        diff = (today - dt).days
        if diff == 0: return "Today"
        if diff == 1: return "Yesterday"
        if diff < 7: return f"{diff} days ago"
        return dt.strftime("%b %d")
    except:
        return str(iso)[:10]

def _post(endpoint, payload):
    try:
        return requests.post(f"{API_URL}{endpoint}", json=payload, timeout=REQUEST_TIMEOUT)
    except requests.exceptions.ConnectionError as e:
        logger.warning("API unreachable: %s", e)
        st.error(f"Connection error: {e}")
    except requests.exceptions.Timeout:
        logger.warning("Request timed out after %s seconds", REQUEST_TIMEOUT)
        st.error(f"Request timed out after {REQUEST_TIMEOUT}s. The LLM is taking too long.")
    except Exception as exc:
        logger.exception("Error: %s", exc)
        st.error(f"Unexpected error: {exc}")
    return None

def _get(endpoint):
    try:
        return requests.get(f"{API_URL}{endpoint}", timeout=10).json()
    except Exception as exc:
        logger.warning("GET failed: %s", exc)
    return None

def ensure_session(user_id, title):
    if st.session_state.get("session_id"):
        return st.session_state["session_id"]
    res = _post("/sessions", {"user_id": user_id, "title": title[:50]})
    if res and res.status_code == 200:
        sid = res.json().get("session_id")
        st.session_state["session_id"] = sid
        return sid
    return None

def _inject_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&display=swap');

    :root {
        --brand-900: #0d1b5e;
        --brand-700: #1a2f8f;
        --brand-500: #3d52c4;
        --brand-300: #7b8fe0;
        --brand-100: #e8ecf9;
        --brand-50: #f3f5fd;
        --surface: #ffffff;
        --bg: #f0f2f9;
        --border: #dde1f0;
        --text-primary: #111827;
        --text-secondary: #6b7280;
        --text-muted: #9ca3af;
        --success-bg: #ecfdf5;
        --success-text: #065f46;
        --success-border: #a7f3d0;
        --warning-bg: #fffbeb;
        --warning-text: #92400e;
        --warning-border: #fde68a;
        --danger-bg: #fff1f2;
        --danger-text: #9f1239;
        --danger-border: #fecdd3;
        --radius-sm: 8px;
        --radius-md: 12px;
        --radius-lg: 16px;
        --shadow-sm: 0 1px 3px rgba(0,0,0,0.08);
    }

    *, *::before, *::after { font-family: 'DM Sans', sans-serif !important; box-sizing: border-box; }
    .stApp { background: var(--bg) !important; }
    #MainMenu, footer, header, .stDeployButton { visibility: hidden; }
    .block-container { padding: 1.25rem 1.75rem !important; max-width: 100% !important; }

    /* Sidebar */
    section[data-testid="stSidebar"],
    section[data-testid="stSidebar"] > div,
    section[data-testid="stSidebar"] > div > div {
        display: block !important;
        visibility: visible !important;
        opacity: 1 !important;
        width: 21rem !important;
        min-width: 21rem !important;
        max-width: 21rem !important;
        transform: none !important;
        left: 0 !important;
        position: relative !important;
        overflow: hidden !important;
    }
    section[data-testid="stSidebar"] {
        background: var(--brand-900) !important;
        border-right: 1px solid rgba(255,255,255,0.06) !important;
        box-shadow: 4px 0 24px rgba(0,0,0,0.18) !important;
    }
    [data-testid="collapsedControl"] { display: none !important; }
    button[kind="header"] { display: none !important; }
    .st-emotion-cache-1dp5vir { display: none !important; }
    [data-testid="stSidebarCollapseButton"] { display: none !important; }
    section[data-testid="stSidebar"] .block-container { padding: 0.4rem 1rem 1rem 1rem !important; overflow: hidden !important; }
    section[data-testid="stSidebar"] * { color: #e8ecf9 !important; max-width: 100% !important; box-sizing: border-box !important; }

    .sb-header { display: flex; align-items: center; gap: 0.6rem; padding-bottom: 0.9rem; border-bottom: 1px solid rgba(255,255,255,0.08); margin-bottom: 0.9rem; overflow: hidden; }
    .sb-logo { width: 62px; height: 62px; background: rgba(255,255,255,0.12); border: 1px solid rgba(255,255,255,0.15); border-radius: var(--radius-sm); display: flex; align-items: center; justify-content: center; font-size: 2.2rem; flex-shrink: 0; }
    .sb-header-text h3 { font-size: 1.5rem !important; font-weight: 700 !important; margin: 0 !important; color: #ffffff !important; }
    .sb-header-text p { font-size: 0.85rem !important; margin: 0.1rem 0 0 !important; color: rgba(255,255,255,0.4) !important; }

    .sb-label { font-size: 0.6rem; text-transform: uppercase; letter-spacing: 1.2px; color: rgba(255,255,255,0.35) !important; margin: 0.75rem 0 0.35rem; padding-left: 0.25rem; }

    .sb-nav-item { display: flex; align-items: center; gap: 0.5rem; padding: 0.4rem 0.6rem; border-radius: var(--radius-sm); font-size: 0.78rem; font-weight: 500; color: rgba(255,255,255,0.65) !important; margin-bottom: 0.15rem; }
    .sb-nav-item.active { background: rgba(255,255,255,0.12); color: white !important; font-weight: 600; }

    .chi { background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.07); border-radius: var(--radius-sm); padding: 0.4rem 0.65rem; margin-bottom: 0.25rem; }
    .chi:hover { background: rgba(255,255,255,0.1); }
    .chi-title { font-size: 0.75rem; font-weight: 500; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .chi-date { font-size: 0.63rem; color: rgba(255,255,255,0.35) !important; margin-top: 0.1rem; }

    .sb-footer { margin-top: 0.75rem; padding-top: 0.75rem; border-top: 1px solid rgba(255,255,255,0.08); }
    .sb-user-row { display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.6rem; }
    .sb-avatar { width: 30px; height: 30px; background: linear-gradient(135deg, var(--brand-500), var(--brand-300)); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.8rem; font-weight: 700; flex-shrink: 0; color: #ffffff !important; }
    .sb-user-name { font-size: 0.78rem; font-weight: 600; color: #ffffff !important; }
    .sb-user-role { font-size: 0.65rem; color: rgba(255,255,255,0.4) !important; margin-top: 0.05rem; }

    /* Buttons */
    .stButton > button { font-family: 'DM Sans', sans-serif !important; border-radius: var(--radius-sm) !important; font-weight: 600 !important; font-size: 0.78rem !important; width: 100% !important; transition: all 0.18s ease !important; background: rgba(255,255,255,0.1) !important; color: #e8ecf9 !important; border: 1px solid rgba(255,255,255,0.15) !important; box-shadow: none !important; padding: 0.4rem 0.75rem !important; }
    .stButton > button:hover { background: rgba(255,255,255,0.18) !important; }

    .btn--primary > button { background: linear-gradient(135deg, var(--brand-700), var(--brand-500)) !important; color: #ffffff !important; border: none !important; box-shadow: 0 3px 10px rgba(61,82,196,0.35) !important; }
    .btn--primary > button:hover { transform: translateY(-1px) !important; }

    .btn--danger > button { background: transparent !important; color: #fca5a5 !important; border: 1px solid rgba(252,165,165,0.3) !important; }
    .btn--danger > button:hover { background: rgba(252,165,165,0.08) !important; }

    .btn--feedback > button, .btn--feedback-active > button { background: var(--brand-50) !important; color: var(--text-secondary) !important; border: 1px solid var(--border) !important; box-shadow: none !important; width: auto !important; padding: 0.3rem 0.7rem !important; font-size: 0.8rem !important; }
    .btn--feedback > button:hover { background: var(--brand-100) !important; color: var(--brand-700) !important; transform: none !important; }
    .btn--feedback-active > button { background: var(--brand-100) !important; color: var(--brand-700) !important; }

    .btn--ticket > button { background: var(--warning-bg) !important; color: var(--warning-text) !important; border: 1px solid var(--warning-border) !important; box-shadow: none !important; width: auto !important; padding: 0.3rem 0.85rem !important; font-size: 0.8rem !important; }

    /* Topbar */
    .chat-topbar { background: var(--surface); border-radius: var(--radius-lg); padding: 1rem 1.5rem; margin-bottom: 1.25rem; display: flex; align-items: center; justify-content: space-between; box-shadow: var(--shadow-sm); border: 1px solid var(--border); }
    .chat-topbar__left { display: flex; align-items: center; gap: 0.85rem; }
    .bot-avatar { width: 42px; height: 42px; background: linear-gradient(135deg, var(--brand-700), var(--brand-300)); border-radius: var(--radius-sm); display: flex; align-items: center; justify-content: center; font-size: 1.2rem; }
    .chat-topbar__name { margin: 0 !important; font-size: 0.95rem !important; font-weight: 700 !important; color: var(--brand-900) !important; }
    .chat-topbar__sub { font-size: 0.74rem; color: var(--text-muted); margin-top: 0.1rem; }
    .status-pill { background: var(--success-bg); color: var(--success-text); border: 1px solid var(--success-border); padding: 0.3rem 0.9rem; border-radius: 20px; font-size: 0.74rem; font-weight: 600; display: flex; align-items: center; gap: 0.4rem; }
    .status-dot { width: 7px; height: 7px; background: #10b981; border-radius: 50%; animation: pulse 1.6s ease-in-out infinite; }
    @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.3} }

    /* Chat window */
    [data-testid="stVerticalBlockBorderWrapper"] { background: var(--surface) !important; border-radius: var(--radius-lg) !important; border: 1px solid var(--border) !important; padding: 1.5rem !important; min-height: 440px !important; box-shadow: var(--shadow-sm) !important; margin-bottom: 1rem !important; }

    /* Bubbles */
    .msg-row { display: flex; margin-bottom: 1.4rem; align-items: flex-end; gap: 0.6rem; }
    .msg-row--user { flex-direction: row-reverse; }
    .msg-avatar { width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.85rem; flex-shrink: 0; }
    .msg-avatar--bot { background: linear-gradient(135deg, var(--brand-700), var(--brand-300)); }
    .msg-avatar--user { background: linear-gradient(135deg, #0891b2, #22d3ee); color: #ffffff; font-weight: 700; }
    .msg-body { display: flex; flex-direction: column; max-width: 65%; }
    .msg-row--user .msg-body { align-items: flex-end; }
    .bubble { padding: 0.8rem 1.1rem; font-size: 0.88rem; line-height: 1.65; word-break: break-word; }
    .bubble--bot { background: var(--brand-50); color: var(--text-primary); border: 1px solid var(--brand-100); border-radius: 4px 16px 16px 16px; box-shadow: var(--shadow-sm); }
    .bubble--user { background: linear-gradient(135deg, var(--brand-700), var(--brand-500)); color: #ffffff; border-radius: 16px 16px 4px 16px; box-shadow: 0 3px 12px rgba(61,82,196,0.28); }
    .msg-time { font-size: 0.67rem; color: var(--text-muted); margin-top: 0.35rem; padding: 0 0.2rem; }

    /* Typing */
    .typing-row { display: flex; align-items: flex-end; gap: 0.6rem; margin-bottom: 1.25rem; }
    .typing-bubble { background: var(--brand-50); border: 1px solid var(--brand-100); border-radius: 4px 16px 16px 16px; padding: 0.8rem 1.1rem; display: flex; align-items: center; gap: 0.4rem; }
    .typing-dot { width: 8px; height: 8px; background: var(--brand-300); border-radius: 50%; animation: wave 1.4s ease-in-out infinite; opacity: 0.6; }
    .typing-dot:nth-child(2) { animation-delay: 0.2s; }
    .typing-dot:nth-child(3) { animation-delay: 0.4s; }
    @keyframes wave { 0%,60%,100%{transform:translateY(0);opacity:0.4} 30%{transform:translateY(-7px);opacity:1} }

    /* Chat input */
    .stChatInput > div { background: var(--surface) !important; border: 2px solid var(--border) !important; border-radius: var(--radius-md) !important; box-shadow: var(--shadow-sm) !important; }
    .stChatInput > div:focus-within { border-color: var(--brand-300) !important; box-shadow: 0 0 0 3px rgba(123,143,224,0.15) !important; }
    .stChatInput textarea { color: var(--text-primary) !important; background: var(--surface) !important; -webkit-text-fill-color: var(--text-primary) !important; font-size: 0.9rem !important; caret-color: var(--brand-500) !important; }
    .stChatInput textarea::placeholder { color: var(--text-muted) !important; }

    /* Selectbox */
    .stSelectbox { width: 75% !important; max-width: 75% !important; }
    .stSelectbox label { color: rgba(255,255,255,0.5) !important; font-size: 0.7rem !important; }
    .stSelectbox > div { width: 100% !important; }
    .stSelectbox > div > div { background: rgba(255,255,255,0.07) !important; border: 1px solid rgba(255,255,255,0.12) !important; border-radius: var(--radius-sm) !important; color: #e8ecf9 !important; width: 100% !important; max-width: 100% !important; box-sizing: border-box !important; min-height: 36px !important; padding: 0.3rem 0.6rem !important; font-size: 1.05rem !important; }
    .stSelectbox > div > div > div { font-size: 1.05rem !important; padding: 0 !important; }

    /* Ticket banner */
    .ticket-banner { background: var(--warning-bg); border: 1.5px solid var(--warning-border); border-radius: var(--radius-md); padding: 1rem 1.25rem; margin-top: 0.75rem; font-size: 0.85rem; color: var(--warning-text); }
    .ticket-banner code { background: rgba(0,0,0,0.06); padding: 0.15rem 0.45rem; border-radius: 4px; font-size: 0.82rem; }
    </style>
    """, unsafe_allow_html=True)


def _render_sidebar(user):
    with st.sidebar:
        st.markdown("""
        <div class="sb-header">
            <div class="sb-logo">&#127891;</div>
            <div class="sb-header-text">
                <h3>NIST Helpdesk</h3>
                <p>AI-powered support</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div class='btn--primary'>", unsafe_allow_html=True)
        if st.button("+ New Chat", key="new_chat"):
            st.session_state.messages = []
            st.session_state.session_id = None
            st.session_state.pop("last_ticket", None)
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

        language = st.selectbox(
            "Language",
            options=list(LANGUAGE_OPTIONS.keys()),
            format_func=lambda x: LANGUAGE_OPTIONS[x],
            key="lang_select",
        )
        st.markdown("<div style='height:0.25rem'></div>", unsafe_allow_html=True)

        st.markdown("<div class='sb-label'>Navigation</div>", unsafe_allow_html=True)

        if user.get("role") not in (None, "guest"):
            if st.button("Dashboard", key="nav_dashboard"):
                st.session_state.screen = "dashboard"
                st.rerun()

        if st.button("FAQs", key="nav_faqs"):
            st.session_state.quick_question = "What are the most frequently asked questions about NIST University?"
            st.rerun()

        # ── User info + Logout (always visible, before history) ──
        initial = safe(user.get("name", "G"))[0].upper()
        name = safe(user.get("name", "Guest"))
        role = safe(user.get("role", "guest")).capitalize()
        uid = safe(str(user.get("id", ""))[:8])
        st.markdown(f"""
        <div class="sb-footer">
            <div class="sb-user-row">
                <div class="sb-avatar">{initial}</div>
                <div>
                    <div class="sb-user-name">{name}</div>
                    <div class="sb-user-role">{role} &middot; #{uid}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div class='btn--danger'>", unsafe_allow_html=True)
        if st.button("Log Out", key="chat_logout"):
            st.session_state.clear()
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div style='height:0.25rem'></div>", unsafe_allow_html=True)

        # ── Recent Conversations ──────────────────────────────────
        user_id = user.get("id")
        if user_id and user_id != "guest":
            st.markdown("<div class='sb-label'>Recent Conversations</div>", unsafe_allow_html=True)
            sessions = _get(f"/sessions/{user_id}") or []
            for s in sessions[:8]:
                date_str = relative_date(s.get("created_at"))
                title = safe(s.get("title", "Untitled"))
                st.markdown(f"""
                <div class="chi">
                    <div class="chi-title">{title}</div>
                    <div class="chi-date">{date_str}</div>
                </div>
                """, unsafe_allow_html=True)
                if st.button("Load", key=f"load_{s['id']}"):
                    msgs = _get(f"/messages/{s['id']}") or []
                    st.session_state.session_id = s["id"]
                    st.session_state.messages = [
                        {"role": m["role"], "content": m["content"], "ts": m.get("created_at")}
                        for m in msgs
                    ]
                    st.rerun()
        else:
            st.markdown("<div style='font-size:0.78rem;color:rgba(255,255,255,0.35);margin-top:0.5rem;'>Log in to save conversation history.</div>", unsafe_allow_html=True)

    return language


def _render_message(index, msg, user):
    role = msg["role"]
    content = safe(msg["content"])
    ts = fmt_time(msg.get("ts")) or datetime.now().strftime("%I:%M %p")

    if role == "user":
        initial = safe(user.get("name", "U"))[0].upper()
        st.markdown(f"""
        <div class="msg-row msg-row--user">
            <div class="msg-avatar msg-avatar--user">{initial}</div>
            <div class="msg-body">
                <div class="bubble bubble--user">{content}</div>
                <div class="msg-time">{ts}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        return

    st.markdown(f"""
    <div class="msg-row">
        <div class="msg-avatar msg-avatar--bot">&#129302;</div>
        <div class="msg-body">
            <div class="bubble bubble--bot">{content}</div>
            <div class="msg-time">{ts}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    feedback_key = f"feedback_{index}"
    current_fb = st.session_state.get(feedback_key)
    col_up, col_down, col_ticket, _ = st.columns([1, 1, 2, 6])
    with col_up:
        cls = "btn--feedback-active" if current_fb == "up" else "btn--feedback"
        st.markdown(f"<div class='{cls}'>", unsafe_allow_html=True)
        if st.button("👍", key=f"up_{index}"):
            st.session_state[feedback_key] = "up"
        st.markdown("</div>", unsafe_allow_html=True)
    with col_down:
        cls = "btn--feedback-active" if current_fb == "down" else "btn--feedback"
        st.markdown(f"<div class='{cls}'>", unsafe_allow_html=True)
        if st.button("👎", key=f"down_{index}"):
            st.session_state[feedback_key] = "down"
        st.markdown("</div>", unsafe_allow_html=True)
    with col_ticket:
        st.markdown("<div class='btn--ticket'>", unsafe_allow_html=True)
        if st.button("Raise Ticket", key=f"ticket_{index}"):
            _raise_ticket(msg["content"], user)
        st.markdown("</div>", unsafe_allow_html=True)


def _raise_ticket(issue, user):
    user_id = user.get("id")
    session_id = st.session_state.get("session_id")
    if not user_id or user_id == "guest":
        st.warning("Please log in to raise a support ticket.")
        return
    if not session_id:
        st.warning("No active session - send a message first.")
        return
    res = _post("/tickets", {
        "user_id": user_id,
        "user_name": safe(user.get("name", "")),
        "session_id": session_id,
        "issue": issue[:200],
    })
    if res and res.status_code == 200:
        st.session_state["last_ticket"] = res.json().get("ticket_id", "")
    else:
        st.error("Failed to raise ticket. Please try again.")


def show():
    user = st.session_state.get("user", {})
    _inject_css()

    # Force sidebar open
    st.markdown("""
    <script>
    window.parent.document.querySelector('[data-testid="collapsedControl"]').click();
    </script>
    """, unsafe_allow_html=True)

    language = _render_sidebar(user)

    st.markdown("""
    <div class="chat-topbar">
        <div class="chat-topbar__left">
            <div class="bot-avatar">&#129302;</div>
            <div>
                <p class="chat-topbar__name">NIST Bot</p>
                <div class="chat-topbar__sub">Ask anything about NIST University</div>
            </div>
        </div>
        <div class="status-pill">
            <span class="status-dot"></span> Online
        </div>
    </div>
    """, unsafe_allow_html=True)

    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "is_loading" not in st.session_state:
        st.session_state.is_loading = False

    with st.container(border=True):
        if not st.session_state.messages:
            st.markdown("""
            <div class="msg-row">
                <div class="msg-avatar msg-avatar--bot">&#129302;</div>
                <div class="msg-body">
                    <div class="bubble bubble--bot">
                        <b>Hello! I am NIST Bot.</b><br><br>
                        I can help you with admissions, fees, hostel, placements, courses, and more.<br><br>
                        What would you like to know?
                    </div>
                    <div class="msg-time">Just now</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        for i, msg in enumerate(st.session_state.messages):
            _render_message(i, msg, user)

    if st.session_state.get("last_ticket"):
        tid = safe(st.session_state["last_ticket"])
        st.markdown(f"""
        <div class="ticket-banner">
            <b>Ticket raised successfully!</b><br>
            Ticket ID: <code>{tid}</code><br>
            Our support team will get back to you shortly.
        </div>
        """, unsafe_allow_html=True)
        del st.session_state["last_ticket"]

    prompt = None
    if not st.session_state.is_loading:
        prompt = st.chat_input("Type your message...")
        if not prompt and st.session_state.get("quick_question"):
            prompt = st.session_state.pop("quick_question")

    if prompt:
        now_iso = datetime.now().isoformat()
        st.session_state.messages.append({"role": "user", "content": prompt, "ts": now_iso})

        user_id = user.get("id")
        if user_id and user_id != "guest":
            ensure_session(user_id, prompt)

        typing_placeholder = st.empty()
        typing_placeholder.markdown("""
        <div class="typing-row">
            <div class="msg-avatar msg-avatar--bot">&#129302;</div>
            <div class="typing-bubble">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        res = _post("/ask-sync", {
            "question": prompt,
            "language": language,
            "session_id": st.session_state.get("session_id"),
            "user_id": user_id,
        })

        typing_placeholder.empty()

        if res is None:
            answer = "⚠️ No response from server. Check the terminal for the actual error above."
        elif res.status_code == 200:
            answer = res.json().get("answer", "No response received.")
        elif res.status_code == 400:
            answer = f"Warning: {safe(res.json().get('detail', 'Bad request.'))}"
        else:
            answer = f"Unexpected error (HTTP {res.status_code}). Please try again."

        st.session_state.messages.append({"role": "assistant", "content": answer, "ts": datetime.now().isoformat()})
        st.session_state.is_loading = False
        st.rerun()
