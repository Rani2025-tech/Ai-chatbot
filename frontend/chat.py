# -*- coding: utf-8 -*-
import html
import logging
from datetime import datetime
import requests
import streamlit as st
import streamlit.components.v1 as components
import os

from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import cm
from reportlab.lib import colors

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

def _headers():
    token = st.session_state.get("token", "").strip()
    return {"Authorization": f"Bearer {token}"} if token else {}

def _post(endpoint, payload):
    try:
        return requests.post(f"{API_URL}{endpoint}", json=payload, headers=_headers(), timeout=REQUEST_TIMEOUT)
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
        return requests.get(f"{API_URL}{endpoint}", headers=_headers(), timeout=10).json()
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

        # Export buttons
        msgs = st.session_state.get("messages", [])
        fname = f"nist_chat_{datetime.now().strftime('%Y%m%d_%H%M')}"
        st.markdown("<div class='sb-label'>Export Chat</div>", unsafe_allow_html=True)
        if msgs:
            st.download_button(
                "⬇ TXT", data=_export_txt(msgs),
                file_name=f"{fname}.txt", mime="text/plain",
                key="export_txt"
            )
            st.download_button(
                "⬇ PDF", data=_export_pdf(msgs),
                file_name=f"{fname}.pdf", mime="application/pdf",
                key="export_pdf"
            )
        else:
            st.caption("Start a chat to enable export")

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

        # User info + Logout
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

        # Recent Conversations
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

    bot_content = msg["content"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    st.markdown(f"""
    <div class="msg-row">
        <div class="msg-avatar msg-avatar--bot">&#129302;</div>
        <div class="msg-body">
            <div class="bubble bubble--bot">{bot_content}</div>
            <div class="msg-time">{ts}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='margin-top:-0.8rem;margin-left:2.5rem;margin-bottom:0.5rem;'>", unsafe_allow_html=True)
    col_ticket, _ = st.columns([1, 9])
    with col_ticket:
        st.markdown("<div class='btn--ticket'>", unsafe_allow_html=True)
        if st.button("Raise Ticket", key=f"ticket_{index}"):
            _raise_ticket(msg["content"], user)
        st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


def _export_txt(messages: list) -> bytes:
    lines = ["NIST University Helpdesk — Chat Export",
             f"Exported: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
             "-" * 50]
    for m in messages:
        role = "You" if m["role"] == "user" else "NIST Bot"
        ts = fmt_time(m.get("ts")) or ""
        lines.append(f"[{ts}] {role}:\n{m['content']}\n")
    return "\n".join(lines).encode("utf-8")


def _export_pdf(messages: list) -> bytes:
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    user_style = ParagraphStyle("user", parent=styles["Normal"],
                                backColor=colors.HexColor("#e8ecf9"),
                                borderPadding=6, fontSize=10,
                                spaceAfter=4, leading=14)
    bot_style  = ParagraphStyle("bot",  parent=styles["Normal"],
                                backColor=colors.HexColor("#f3f5fd"),
                                borderPadding=6, fontSize=10,
                                spaceAfter=4, leading=14)
    title_style = ParagraphStyle("title", parent=styles["Heading1"],
                                 fontSize=14, spaceAfter=4)
    story = [
        Paragraph("NIST University Helpdesk — Chat Export", title_style),
        Paragraph(f"Exported: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles["Normal"]),
        Spacer(1, 0.4*cm),
    ]
    for m in messages:
        role = "You" if m["role"] == "user" else "NIST Bot"
        ts = fmt_time(m.get("ts")) or ""
        label = f"<b>{role}</b>  <font size=8 color=grey>{ts}</font>"
        text  = m["content"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        style = user_style if m["role"] == "user" else bot_style
        story += [Paragraph(label, styles["Normal"]), Paragraph(text, style), Spacer(1, 0.2*cm)]
    doc.build(story)
    return buf.getvalue()


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

            chips = ["Admission info", "Fee structure", "Hostel details", "Placement records", "Course details"]
            st.markdown("""
            <style>
            div[data-testid="stHorizontalBlock"] > div[data-testid="column"] .stButton > button {
                background: #3d2fa0 !important;
                color: #ffffff !important;
                -webkit-text-fill-color: #ffffff !important;
                border: none !important;
                border-radius: 50px !important;
                padding: 1px 5px !important;
                font-size: 7px !important;
                font-weight: 500 !important;
                width: auto !important;
                min-width: 0 !important;
                height: 14px !important;
                line-height: 1 !important;
                box-shadow: none !important;
                cursor: pointer !important;
                white-space: nowrap !important;
            }
            div[data-testid="stHorizontalBlock"] > div[data-testid="column"] .stButton > button:hover {
                background: #2d1f8f !important;
                transform: none !important;
            }
            </style>
            """, unsafe_allow_html=True)
            cols = st.columns(len(chips))
            for i, chip in enumerate(chips):
                with cols[i]:
                    if st.button(chip, key=f"chip_{i}"):
                        st.session_state.quick_question = chip
                        st.rerun()

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

        # Inject mic button + sidebar toggle button via JS
        components.html("""
        <script>
        function injectButtons() {
            const doc = window.parent.document;

            // ── Sidebar Toggle Button (hamburger, fixed top-left) ──────────
            if (!doc.getElementById('sidebarToggleBtn')) {
                const btn = doc.createElement('button');
                btn.id = 'sidebarToggleBtn';
                btn.innerHTML = '&#9776;';
                btn.title = 'Toggle Sidebar';
                btn.style.cssText = `
                    position: fixed;
                    top: 14px;
                    left: 14px;
                    z-index: 99999;
                    width: 40px;
                    height: 40px;
                    border-radius: 10px;
                    border: none;
                    background: #1E2A6E;
                    color: #ffffff;
                    font-size: 20px;
                    cursor: pointer;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.3);
                    transition: background 0.2s;
                `;
                btn.onmouseover = () => btn.style.background = '#3d52c4';
                btn.onmouseout  = () => btn.style.background = '#1E2A6E';
                btn.onclick = () => {
                    const collapseBtn = doc.querySelector('[data-testid="collapsedControl"] button') ||
                                       doc.querySelector('[data-testid="collapsedControl"]') ||
                                       doc.querySelector('[data-testid="stSidebarCollapseButton"] button');
                    if (collapseBtn) collapseBtn.click();
                };
                doc.body.appendChild(btn);
            }

            // ── Close button inside sidebar ─────────────────────────
            const sidebar = doc.querySelector('[data-testid="stSidebar"]');
            if (sidebar && !doc.getElementById('sidebarCloseBtn')) {
                const closeBtn = doc.createElement('button');
                closeBtn.id = 'sidebarCloseBtn';
                closeBtn.innerHTML = '&#10005;';
                closeBtn.title = 'Close Sidebar';
                closeBtn.style.cssText = `
                    position: absolute;
                    top: 12px;
                    right: 12px;
                    z-index: 99999;
                    width: 30px;
                    height: 30px;
                    border-radius: 8px;
                    border: 1px solid rgba(255,255,255,0.2);
                    background: rgba(255,255,255,0.1);
                    color: #ffffff;
                    font-size: 14px;
                    cursor: pointer;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    transition: background 0.2s;
                `;
                closeBtn.onmouseover = () => closeBtn.style.background = 'rgba(255,255,255,0.25)';
                closeBtn.onmouseout  = () => closeBtn.style.background = 'rgba(255,255,255,0.1)';
                closeBtn.onclick = () => {
                    const collapseBtn = doc.querySelector('[data-testid="stSidebarCollapseButton"] button') ||
                                       doc.querySelector('[data-testid="collapsedControl"] button') ||
                                       doc.querySelector('[data-testid="collapsedControl"]');
                    if (collapseBtn) collapseBtn.click();
                };
                sidebar.style.position = 'relative';
                sidebar.appendChild(closeBtn);
            }

            // ── Mic Button ───────────────────────────────────
            const chatInput = doc.querySelector('.stChatInput');
            if (!chatInput || doc.getElementById('micBtn')) return;

            const micBtn = doc.createElement('button');
            micBtn.id = 'micBtn';
            micBtn.innerHTML = '&#127908;';
            micBtn.title = 'Click to speak';
            micBtn.style.cssText = `
                width:38px;height:38px;min-width:38px;border-radius:50%;border:none;
                background:linear-gradient(135deg,#93c5fd,#60a5fa);
                color:white;font-size:16px;cursor:pointer;
                display:flex;align-items:center;justify-content:center;
                box-shadow:0 2px 8px rgba(96,165,250,0.5);
                transition:all 0.2s;flex-shrink:0;margin-right:6px;
                position:relative;z-index:999;
            `;

            let recognition = null;
            let listening = false;

            micBtn.onclick = function() {
                if (!('webkitSpeechRecognition' in window.parent) && !('SpeechRecognition' in window.parent)) {
                    alert('Speech recognition not supported. Use Chrome or Edge.');
                    return;
                }
                if (listening) { recognition.stop(); return; }
                const SR = window.parent.SpeechRecognition || window.parent.webkitSpeechRecognition;
                recognition = new SR();
                recognition.lang = 'en-IN';
                recognition.interimResults = true;
                recognition.continuous = false;
                recognition.onstart = () => {
                    listening = true;
                    micBtn.style.background = 'linear-gradient(135deg,#e53e3e,#c53030)';
                    micBtn.innerHTML = '&#9209;';
                    micBtn.title = 'Stop listening';
                };
                recognition.onresult = (e) => {
                    let transcript = '';
                    for (let i = 0; i < e.results.length; i++) transcript += e.results[i][0].transcript;
                    const textarea = doc.querySelector('.stChatInput textarea');
                    if (textarea) {
                        const setter = Object.getOwnPropertyDescriptor(window.parent.HTMLTextAreaElement.prototype, 'value').set;
                        setter.call(textarea, transcript);
                        textarea.dispatchEvent(new window.parent.Event('input', { bubbles: true }));
                        textarea.focus();
                    }
                };
                recognition.onend = () => {
                    listening = false;
                    micBtn.style.background = 'linear-gradient(135deg,#93c5fd,#60a5fa)';
                    micBtn.innerHTML = '&#127908;';
                    micBtn.title = 'Click to speak';
                };
                recognition.onerror = () => {
                    listening = false;
                    micBtn.style.background = 'linear-gradient(135deg,#93c5fd,#60a5fa)';
                    micBtn.innerHTML = '&#127908;';
                };
                recognition.start();
            };

            const sendBtn = chatInput.querySelector('button');
            if (sendBtn && sendBtn.parentNode) sendBtn.parentNode.insertBefore(micBtn, sendBtn);
        }

        const interval = setInterval(() => {
            injectButtons();
            if (window.parent.document.getElementById('micBtn') &&
                window.parent.document.getElementById('sidebarToggleBtn')) clearInterval(interval);
        }, 300);
        </script>
        """, height=0)

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

        full_answer = ""
        try:
            stream_res = requests.post(
                f"{API_URL}/ask-stream",
                json={"question": prompt, "language": language,
                      "session_id": st.session_state.get("session_id"), "user_id": user_id},
                headers=_headers(),
                stream=True,
                timeout=REQUEST_TIMEOUT
            )
            typing_placeholder.empty()
            if stream_res.status_code == 200:
                stream_placeholder = st.empty()
                for chunk in stream_res.iter_content(chunk_size=None, decode_unicode=True):
                    if chunk:
                        full_answer += chunk
                        stream_placeholder.markdown(f"""
                        <div class="msg-row">
                            <div class="msg-avatar msg-avatar--bot">&#129302;</div>
                            <div class="msg-body">
                                <div class="bubble bubble--bot">{full_answer.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')}▌</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                stream_placeholder.empty()
            else:
                full_answer = f"⚠️ Error {stream_res.status_code}. Please try again."
        except Exception:
            typing_placeholder.empty()
            res = _post("/ask-sync", {
                "question": prompt, "language": language,
                "session_id": st.session_state.get("session_id"), "user_id": user_id,
            })
            if res is None:
                full_answer = "⚠️ No response from server. Check the terminal for the actual error above."
            elif res.status_code == 200:
                full_answer = html.unescape(res.json().get("answer", "No response received."))
            elif res.status_code == 400:
                full_answer = f"Warning: {safe(res.json().get('detail', 'Bad request.'))}"
            else:
                full_answer = f"Unexpected error (HTTP {res.status_code}). Please try again."

        st.session_state.messages.append({"role": "assistant", "content": full_answer, "ts": datetime.now().isoformat()})
        if st.session_state.get("session_id") and user_id and user_id != "guest" and full_answer:
            _post("/save-message", {
                "session_id": st.session_state["session_id"],
                "user_id": user_id,
                "question": prompt,
                "answer": full_answer,
            })
        st.session_state.is_loading = False
        st.rerun()
