import streamlit as st
import requests
import os

API_URL = os.getenv("API_URL", "http://localhost:8000/api")

def show():
    user = st.session_state.get("user", {})

    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    * { font-family: 'Inter', sans-serif !important; }

    .stApp { background: #f5f6fa; }
    #MainMenu, footer, header, .stDeployButton { visibility: hidden; }
    .block-container { padding: 2rem 2.5rem !important; max-width: 1200px !important; }

    .admin-header {
        background: linear-gradient(135deg, #1a237e, #283593);
        border-radius: 20px;
        padding: 1.5rem 2rem;
        color: white;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .admin-header h2 {
        font-size: 1.4rem !important;
        font-weight: 700 !important;
        margin: 0 !important;
        color: white !important;
    }
    .admin-header p {
        color: rgba(255,255,255,0.7) !important;
        margin: 0.2rem 0 0 0 !important;
        font-size: 0.85rem !important;
    }

    .stat-card {
        background: white;
        border-radius: 14px;
        padding: 1.25rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.06);
        text-align: center;
        border-top: 4px solid #3f51b5;
    }
    .stat-value { font-size: 2rem; font-weight: 700; color: #3f51b5; }
    .stat-label { font-size: 0.75rem; color: #757575; text-transform: uppercase; letter-spacing: 0.5px; margin-top: 0.2rem; }

    .section-card {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        margin-bottom: 1.5rem;
    }
    .section-card h4 {
        font-size: 1rem !important;
        font-weight: 600 !important;
        color: #212121 !important;
        margin: 0 0 1rem 0 !important;
        padding-bottom: 0.75rem !important;
        border-bottom: 1px solid #f0f0f0 !important;
    }

    .ticket-row {
        display: flex;
        align-items: center;
        padding: 0.75rem 0;
        border-bottom: 1px solid #f5f5f5;
        gap: 1rem;
        font-size: 0.85rem;
    }
    .ticket-id { font-weight: 600; color: #3f51b5; min-width: 110px; }
    .ticket-user { color: #424242; min-width: 100px; }
    .ticket-issue { color: #616161; flex: 1; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .ticket-date { color: #9e9e9e; min-width: 90px; font-size: 0.75rem; }

    .badge-open {
        background: #fff3e0; color: #e65100;
        padding: 0.2rem 0.6rem; border-radius: 20px;
        font-size: 0.75rem; font-weight: 600; min-width: 70px; text-align: center;
    }
    .badge-resolved {
        background: #e8f5e9; color: #2e7d32;
        padding: 0.2rem 0.6rem; border-radius: 20px;
        font-size: 0.75rem; font-weight: 600; min-width: 70px; text-align: center;
    }

    .stButton > button {
        background: linear-gradient(135deg, #3f51b5, #5c6bc0) !important;
        color: white !important; border: none !important;
        border-radius: 10px !important; padding: 0.6rem 1rem !important;
        font-weight: 600 !important; font-size: 0.85rem !important;
        width: 100% !important; transition: all 0.2s !important;
        box-shadow: 0 3px 10px rgba(63,81,181,0.25) !important;
    }
    .stButton > button:hover { transform: translateY(-1px) !important; }

    .logout-btn > button {
        background: white !important; color: #f44336 !important;
        border: 1.5px solid #f44336 !important; box-shadow: none !important;
    }
    .resolve-btn > button {
        background: #e8f5e9 !important; color: #2e7d32 !important;
        border: none !important; box-shadow: none !important;
        padding: 0.3rem 0.6rem !important; font-size: 0.75rem !important;
    }

    .stTextInput input {
        border: 1.5px solid #e0e0e0 !important; border-radius: 10px !important;
        color: #212121 !important; background: #fafafa !important;
    }
    .stTextInput label { color: #424242 !important; font-size: 0.85rem !important; font-weight: 500 !important; }

    .stFileUploader {
        background: #f8f9ff !important;
        border: 2px dashed #7986cb !important;
        border-radius: 12px !important;
    }
    .stSuccess { border-radius: 10px !important; }
    .stError { border-radius: 10px !important; }
    </style>
    """, unsafe_allow_html=True)

    # Header
    st.markdown(f"""
    <div class="admin-header">
        <div>
            <h2>🛡️ Admin Panel</h2>
            <p>Welcome, {user.get('name', 'Admin')} — Manage documents, tickets and users</p>
        </div>
        <div style="font-size:3rem;">⚙️</div>
    </div>
    """, unsafe_allow_html=True)

    # Stats
    try:
        stats = requests.get(f"{API_URL}/stats").json()
    except:
        stats = {"total_users": 0, "total_tickets": 0, "open_tickets": 0, "resolved_tickets": 0, "total_messages": 0}

    c1, c2, c3, c4, c5 = st.columns(5)
    for col, val, label, color in [
        (c1, stats.get("total_users", 0), "Total Users", "#3f51b5"),
        (c2, stats.get("total_messages", 0), "Messages", "#9c27b0"),
        (c3, stats.get("total_tickets", 0), "Total Tickets", "#ff9800"),
        (c4, stats.get("open_tickets", 0), "Open", "#f44336"),
        (c5, stats.get("resolved_tickets", 0), "Resolved", "#4caf50"),
    ]:
        with col:
            st.markdown(f"""
            <div class="stat-card" style="border-top-color:{color};">
                <div class="stat-value" style="color:{color};">{val}</div>
                <div class="stat-label">{label}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    col_left, col_right = st.columns([1.2, 2])

    # ── Left: Upload Documents ────────────────────────────────────
    with col_left:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("<h4>📄 Upload Documents</h4>", unsafe_allow_html=True)

        uploaded_file = st.file_uploader("Choose a PDF", type="pdf", label_visibility="collapsed")
        if uploaded_file:
            if st.button("🚀 Process & Index"):
                with st.spinner("Indexing..."):
                    try:
                        files = {"file": (uploaded_file.name, uploaded_file, "application/pdf")}
                        res = requests.post(f"{API_URL}/upload", files=files)
                        if res.status_code == 200:
                            data = res.json()
                            st.success(f"✅ {uploaded_file.name} indexed! ({data['chunks_created']} chunks)")
                        else:
                            st.error(f"❌ {res.json()['detail']}")
                    except Exception as e:
                        st.error(f"❌ {str(e)}")

        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
        st.markdown("<h4 style='font-size:0.9rem;font-weight:600;color:#424242;margin-bottom:0.5rem;'>📚 Indexed Documents</h4>", unsafe_allow_html=True)
        try:
            docs = requests.get(f"{API_URL}/documents").json()
            if docs["total"] == 0:
                st.markdown("<div style='color:#9e9e9e;font-size:0.85rem;'>No documents yet.</div>", unsafe_allow_html=True)
            else:
                for doc in docs["documents"]:
                    st.markdown(f"""
                    <div style="background:#f8f9ff;border-left:3px solid #3f51b5;border-radius:8px;
                                padding:0.5rem 0.75rem;margin-bottom:0.4rem;font-size:0.82rem;color:#424242;">
                        📄 {doc}
                    </div>
                    """, unsafe_allow_html=True)
        except:
            st.warning("⚠️ Cannot load documents")

        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
        st.markdown("<div class='logout-btn'>", unsafe_allow_html=True)
        if st.button("🚪 Logout"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Right: Tickets ────────────────────────────────────────────
    with col_right:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("<h4>🎫 Support Tickets</h4>", unsafe_allow_html=True)

        search = st.text_input("🔍 Search tickets", placeholder="Search by user or issue...", label_visibility="collapsed", key="ticket_search")

        try:
            tickets = requests.get(f"{API_URL}/tickets").json()
        except:
            tickets = []

        if search:
            tickets = [t for t in tickets if search.lower() in t.get("user_name", "").lower()
                       or search.lower() in t.get("issue", "").lower()]

        filter_col1, filter_col2 = st.columns(2)
        with filter_col1:
            status_filter = st.selectbox("Status", ["All", "open", "resolved"], label_visibility="collapsed", key="status_filter")
        with filter_col2:
            st.markdown(f"<div style='color:#757575;font-size:0.85rem;padding-top:0.5rem;'>{len(tickets)} tickets found</div>", unsafe_allow_html=True)

        if status_filter != "All":
            tickets = [t for t in tickets if t.get("status") == status_filter]

        if not tickets:
            st.markdown("<div style='color:#9e9e9e;font-size:0.85rem;text-align:center;padding:2rem;'>No tickets found.</div>", unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="ticket-row" style="font-weight:600;color:#424242;border-bottom:2px solid #e0e0e0;">
                <div style="min-width:110px;">Ticket ID</div>
                <div style="min-width:100px;">User</div>
                <div style="flex:1;">Issue</div>
                <div style="min-width:70px;">Status</div>
                <div style="min-width:90px;">Date</div>
                <div style="min-width:80px;">Action</div>
            </div>
            """, unsafe_allow_html=True)

            for t in tickets:
                badge = f'<span class="badge-open">🔴 Open</span>' if t["status"] == "open" else f'<span class="badge-resolved">🟢 Done</span>'
                date = t["created_at"][:10] if t.get("created_at") else ""
                st.markdown(f"""
                <div class="ticket-row">
                    <div class="ticket-id">{t['id']}</div>
                    <div class="ticket-user">{t.get('user_name','—')}</div>
                    <div class="ticket-issue" title="{t['issue']}">{t['issue'][:60]}...</div>
                    <div>{badge}</div>
                    <div class="ticket-date">{date}</div>
                </div>
                """, unsafe_allow_html=True)

                if t["status"] == "open":
                    st.markdown("<div class='resolve-btn'>", unsafe_allow_html=True)
                    if st.button("✅ Resolve", key=f"resolve_{t['id']}"):
                        try:
                            requests.patch(f"{API_URL}/tickets/{t['id']}", json={"status": "resolved"})
                            st.rerun()
                        except:
                            st.error("Failed to update")
                    st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)
