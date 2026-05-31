import streamlit as st
import requests
from datetime import datetime

st.set_page_config(page_title="Home — NIST Helpdesk", page_icon="🏠", layout="wide")

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

/* Cards */
.dash-card {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1rem;
}
.dash-card-title {
    color: rgba(255,255,255,0.5);
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 0.75rem;
}

/* Announcement */
.announcement {
    background: rgba(102,126,234,0.1);
    border-left: 3px solid #667eea;
    border-radius: 8px;
    padding: 0.75rem 1rem;
    margin-bottom: 0.6rem;
    color: rgba(255,255,255,0.85) !important;
    font-size: 0.85rem !important;
}
.announcement .ann-date {
    color: rgba(255,255,255,0.4);
    font-size: 0.72rem;
    margin-top: 0.2rem;
}

/* Quick action buttons */
.stButton > button {
    background: rgba(255,255,255,0.06) !important;
    color: white !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 12px !important;
    padding: 0.9rem 1rem !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    width: 100% !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    background: rgba(102,126,234,0.2) !important;
    border-color: rgba(102,126,234,0.5) !important;
    transform: translateY(-2px) !important;
}

/* Class item */
.class-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: rgba(255,255,255,0.04);
    border-radius: 10px;
    padding: 0.6rem 0.9rem;
    margin-bottom: 0.5rem;
    font-size: 0.85rem;
    color: rgba(255,255,255,0.8) !important;
}
.class-time { color: #667eea; font-weight: 600; font-size: 0.8rem; }

/* Task item */
.task-item {
    background: rgba(255,255,255,0.04);
    border-left: 3px solid #f093fb;
    border-radius: 8px;
    padding: 0.6rem 0.9rem;
    margin-bottom: 0.5rem;
    font-size: 0.85rem;
    color: rgba(255,255,255,0.8) !important;
}
.task-due { color: rgba(245,101,101,0.9); font-size: 0.75rem; }

/* Notification */
.notif-item {
    background: rgba(255,255,255,0.04);
    border-radius: 10px;
    padding: 0.6rem 0.9rem;
    margin-bottom: 0.5rem;
    font-size: 0.82rem;
    color: rgba(255,255,255,0.75) !important;
    display: flex;
    gap: 0.6rem;
    align-items: flex-start;
}

/* Search */
.stTextInput > div > div > input {
    background: rgba(255,255,255,0.07) !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    border-radius: 50px !important;
    color: white !important;
    font-size: 1rem !important;
    padding: 0.75rem 1.5rem !important;
}
.stTextInput > div > div > input::placeholder { color: rgba(255,255,255,0.35) !important; }
.stTextInput label { display: none !important; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(15,12,41,0.95), rgba(48,43,99,0.95)) !important;
    border-right: 1px solid rgba(255,255,255,0.08) !important;
}

#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── Greeting ─────────────────────────────────────────────────────
hour = datetime.now().hour
greeting = "Good morning" if hour < 12 else "Good afternoon" if hour < 17 else "Good evening"

st.markdown(f"""
<div style="margin-bottom:1.5rem;">
    <div style="color:rgba(255,255,255,0.45);font-size:0.9rem;">{greeting} 👋</div>
    <div style="color:white;font-size:2rem;font-weight:700;line-height:1.2;">Welcome to NIST Helpdesk</div>
    <div style="color:rgba(255,255,255,0.4);font-size:0.85rem;margin-top:0.3rem;">
        {datetime.now().strftime("%A, %d %B %Y")}
    </div>
</div>
""", unsafe_allow_html=True)

# ── Search Bar ────────────────────────────────────────────────────
search = st.text_input("", placeholder="🔍  Ask anything about NIST University...", key="home_search")
if search:
    st.switch_page("pages/2_🤖_AI_Chat.py")

st.markdown("<br>", unsafe_allow_html=True)

# ── AI Chat CTA ───────────────────────────────────────────────────
st.markdown("""
<div style="background:linear-gradient(135deg,rgba(102,126,234,0.2),rgba(240,147,251,0.15));
            border:1px solid rgba(102,126,234,0.35);border-radius:20px;
            padding:1.5rem 2rem;margin-bottom:1.5rem;
            display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:1rem;">
    <div>
        <div style="color:white;font-size:1.2rem;font-weight:700;">🤖 AI Chat Assistant</div>
        <div style="color:rgba(255,255,255,0.55);font-size:0.85rem;margin-top:0.3rem;">
            Ask about fees, admissions, placements, hostel & more
        </div>
    </div>
</div>
""", unsafe_allow_html=True)
if st.button("💬 Open AI Chat →", key="open_chat"):
    st.switch_page("pages/2_🤖_AI_Chat.py")

st.markdown("<br>", unsafe_allow_html=True)

# ── Row 1: Quick Actions + Announcements ─────────────────────────
col_actions, col_ann = st.columns([1, 1.6])

with col_actions:
    st.markdown('<div class="dash-card">', unsafe_allow_html=True)
    st.markdown('<div class="dash-card-title">⚡ Quick Actions</div>', unsafe_allow_html=True)
    qa1, qa2 = st.columns(2)
    with qa1:
        if st.button("📝\nApply for Leave", key="qa_leave"):
            st.info("Leave application feature coming soon!")
        if st.button("🏦\nFee Payment", key="qa_fee"):
            st.info("Fee payment portal coming soon!")
    with qa2:
        if st.button("📅\nCheck Timetable", key="qa_tt"):
            st.info("Timetable feature coming soon!")
        if st.button("📣\nRaise Complaint", key="qa_complaint"):
            st.info("Complaint portal coming soon!")
    st.markdown('</div>', unsafe_allow_html=True)

with col_ann:
    st.markdown('<div class="dash-card">', unsafe_allow_html=True)
    st.markdown('<div class="dash-card-title">📢 Announcements</div>', unsafe_allow_html=True)
    announcements = [
        ("🗓️ Last date for fee payment: 30 June 2025", "Finance Dept · 2 days ago"),
        ("📋 End semester exam schedule released", "Exam Cell · 3 days ago"),
        ("🏆 Placement drive: TCS on 5th July 2025", "Placement Cell · 4 days ago"),
        ("🎓 Convocation ceremony: 15 July 2025", "Admin · 1 week ago"),
        ("📚 Library extended hours during exams", "Library · 1 week ago"),
    ]
    for text, date in announcements:
        st.markdown(f"""
        <div class="announcement">
            {text}
            <div class="ann-date">{date}</div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ── Row 2: Today's Classes + Pending Tasks + Notifications ────────
col_cls, col_tasks, col_notif = st.columns(3)

with col_cls:
    st.markdown('<div class="dash-card">', unsafe_allow_html=True)
    st.markdown('<div class="dash-card-title">📖 Today\'s Classes</div>', unsafe_allow_html=True)
    classes = [
        ("Data Structures", "09:00 AM", "Room 301"),
        ("DBMS", "11:00 AM", "Room 204"),
        ("OS Lab", "02:00 PM", "Lab 102"),
        ("Computer Networks", "04:00 PM", "Room 301"),
    ]
    for subject, time, room in classes:
        st.markdown(f"""
        <div class="class-item">
            <div>
                <div>{subject}</div>
                <div style="color:rgba(255,255,255,0.4);font-size:0.75rem;">{room}</div>
            </div>
            <div class="class-time">{time}</div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_tasks:
    st.markdown('<div class="dash-card">', unsafe_allow_html=True)
    st.markdown('<div class="dash-card-title">✅ Pending Tasks</div>', unsafe_allow_html=True)
    tasks = [
        ("Submit DBMS Assignment", "Due: Today"),
        ("Pay semester fees", "Due: 30 June"),
        ("Register for electives", "Due: 25 June"),
        ("Upload internship report", "Due: 28 June"),
    ]
    for task, due in tasks:
        st.markdown(f"""
        <div class="task-item">
            <div>{task}</div>
            <div class="task-due">{due}</div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_notif:
    st.markdown('<div class="dash-card">', unsafe_allow_html=True)
    st.markdown('<div class="dash-card-title">🔔 Notifications</div>', unsafe_allow_html=True)
    notifications = [
        ("🟢", "Your leave application was approved"),
        ("🔵", "New study material uploaded in DBMS"),
        ("🟡", "Reminder: Fee payment deadline in 5 days"),
        ("🔴", "Attendance below 75% in CN — attend classes"),
        ("🟢", "Internship certificate verified"),
    ]
    for icon, text in notifications:
        st.markdown(f"""
        <div class="notif-item">
            <span>{icon}</span>
            <span>{text}</span>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
