import streamlit as st
import requests
import os

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000/api")

def show():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&display=swap');
    *, *::before, *::after { font-family: 'DM Sans', sans-serif !important; box-sizing: border-box; }

    .stApp { background: linear-gradient(135deg, #e8eaf6 0%, #e3f2fd 100%) !important; min-height: 100vh; }
    #MainMenu, footer, header, .stDeployButton { visibility: hidden; }
    .block-container { padding: 4rem 1rem !important; max-width: 480px !important; margin: 0 auto !important; }

    .brand-wrap { text-align: center; margin-bottom: 2rem; }
    .brand-icon {
        width: 72px; height: 72px;
        background: linear-gradient(135deg, #1a2f8f, #3d52c4);
        border-radius: 20px;
        display: flex; align-items: center; justify-content: center;
        font-size: 2rem; margin: 0 auto 1rem;
        box-shadow: 0 8px 24px rgba(61,82,196,0.3);
    }
    .brand-wrap h1 { font-size: 1.7rem !important; font-weight: 700 !important; color: #0d1b5e !important; margin: 0 !important; }
    .brand-wrap p { color: #6b7280 !important; font-size: 0.9rem !important; margin: 0.3rem 0 0 !important; }

    /* Radio tabs */
    div[data-testid="stRadio"] > div {
        gap: 0 !important;
        background: #f3f5fd;
        border-radius: 10px;
        padding: 4px;
        display: flex !important;
    }
    div[data-testid="stRadio"] label {
        flex: 1 !important;
        background: transparent !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.45rem 1rem !important;
        font-weight: 500 !important;
        font-size: 0.88rem !important;
        text-align: center !important;
        cursor: pointer !important;
        color: #374151 !important;
        -webkit-text-fill-color: #374151 !important;
        transition: all 0.2s !important;
    }
    div[data-testid="stRadio"] label:has(input:checked) {
        background: white !important;
        color: #1a2f8f !important;
        -webkit-text-fill-color: #1a2f8f !important;
        font-weight: 600 !important;
        box-shadow: 0 1px 4px rgba(0,0,0,0.1) !important;
    }
    div[data-testid="stRadio"] input { display: none !important; }
    div[data-testid="stRadio"] p {
        color: inherit !important;
        -webkit-text-fill-color: inherit !important;
        margin: 0 !important;
    }

    /* Inputs */
    .stTextInput input {
        border: 1.5px solid #e8ecf9 !important;
        border-radius: 10px !important;
        font-size: 0.92rem !important;
        color: #111827 !important;
        background: #fafbff !important;
        -webkit-text-fill-color: #111827 !important;
        padding: 0.65rem 1rem !important;
    }
    .stTextInput input:focus { border-color: #3d52c4 !important; box-shadow: 0 0 0 3px rgba(61,82,196,0.1) !important; }
    .stTextInput label { color: #374151 !important; font-size: 0.83rem !important; font-weight: 500 !important; -webkit-text-fill-color: #374151 !important; }

    /* Primary button */
    .stButton > button {
        background: linear-gradient(135deg, #1a2f8f, #3d52c4) !important;
        color: white !important; border: none !important;
        border-radius: 10px !important; padding: 0.7rem 1rem !important;
        font-weight: 600 !important; font-size: 0.92rem !important;
        width: 100% !important;
        box-shadow: 0 4px 14px rgba(61,82,196,0.3) !important;
        transition: all 0.2s !important;
    }
    .stButton > button:hover { transform: translateY(-1px) !important; box-shadow: 0 6px 20px rgba(61,82,196,0.4) !important; }

    /* Guest button — targets the second button by key name via aria-label */
    button[kind="secondary"],
    [data-testid="btn_guest"] > button {
        background: white !important;
        color: #3d52c4 !important;
        border: 1.5px solid #c7d0f5 !important;
        box-shadow: none !important;
    }

    .divider { text-align: center; color: #9ca3af; font-size: 0.82rem; margin: 1rem 0; position: relative; }
    .divider::before, .divider::after { content: ''; position: absolute; top: 50%; width: 44%; height: 1px; background: #e5e7eb; }
    .divider::before { left: 0; } .divider::after { right: 0; }

    .stSuccess, .stError, .stWarning { border-radius: 10px !important; font-size: 0.84rem !important; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="brand-wrap">
        <div class="brand-icon">🎓</div>
        <h1>NIST Helpdesk</h1>
        <p>AI-powered support, instantly</p>
    </div>
    """, unsafe_allow_html=True)

    tab = st.radio("", ["Login", "Sign Up"], horizontal=True, label_visibility="collapsed")

    if tab == "Login":
        email = st.text_input("Email address", placeholder="you@example.com", key="login_email")
        password = st.text_input("Password", type="password", placeholder="••••••••", key="login_pass")
        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

        if st.button("Login", key="btn_login"):
            if not email or not password:
                st.error("Please fill in all fields")
            else:
                try:
                    res = requests.post(f"{API_URL}/auth/login", json={"email": email, "password": password})
                    if res.status_code == 200:
                        user = res.json()
                        st.session_state.user = user
                        st.session_state.screen = "admin" if user["role"] == "admin" else "dashboard"
                        st.rerun()
                    else:
                        st.error(res.json().get("detail", "Login failed"))
                except Exception as e:
                    st.error(f"❌ Cannot connect to server: {e}")

        st.markdown("<div class='divider'>or</div>", unsafe_allow_html=True)

        if st.button("Continue as Guest", key="btn_guest", type="secondary"):
            st.session_state.user = {"id": "guest", "name": "Guest", "role": "guest"}
            st.session_state.screen = "chat"
            st.session_state.messages = []
            st.session_state.session_id = None
            st.rerun()

    else:
        name = st.text_input("Full Name", placeholder="Your full name", key="signup_name")
        email = st.text_input("Email address", placeholder="you@example.com", key="signup_email")
        password = st.text_input("Password", type="password", placeholder="Min 6 characters", key="signup_pass")
        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

        if st.button("Create Account", key="btn_signup"):
            if not name or not email or not password:
                st.error("Please fill in all fields")
            elif len(password) < 6:
                st.error("Password must be at least 6 characters")
            else:
                try:
                    res = requests.post(f"{API_URL}/auth/signup", json={"name": name, "email": email, "password": password})
                    if res.status_code == 200:
                        st.success("✅ Account created! Please login.")
                    else:
                        st.error(res.json().get("detail", "Signup failed"))
                except Exception as e:
                    st.error(f"❌ Cannot connect to server: {e}")