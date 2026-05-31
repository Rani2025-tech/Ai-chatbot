import streamlit as st
import requests
import os

API_URL = os.getenv("API_URL", "http://localhost:8000/api")

def show_login():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    * { font-family: 'Inter', sans-serif !important; }

    .stApp {
        background: linear-gradient(135deg, #e8eaf6 0%, #e3f2fd 100%);
        min-height: 100vh;
    }

    #MainMenu, footer, header, .stDeployButton { visibility: hidden; }

    .login-card {
        background: white;
        border-radius: 20px;
        padding: 2.5rem 2rem;
        box-shadow: 0 8px 40px rgba(63,81,181,0.12);
        max-width: 420px;
        margin: 0 auto;
    }

    .login-logo {
        text-align: center;
        margin-bottom: 1.5rem;
    }

    .login-logo h1 {
        font-size: 1.8rem !important;
        font-weight: 700 !important;
        color: #3f51b5 !important;
        margin: 0.5rem 0 0 0 !important;
    }

    .login-logo p {
        color: #757575 !important;
        font-size: 0.9rem !important;
        margin: 0.25rem 0 0 0 !important;
    }

    .tab-btn {
        display: inline-block;
        padding: 0.5rem 1.5rem;
        border-radius: 8px;
        font-weight: 600;
        font-size: 0.9rem;
        cursor: pointer;
        border: none;
        transition: all 0.2s;
    }

    .stTextInput input {
        border: 1.5px solid #e0e0e0 !important;
        border-radius: 10px !important;
        padding: 0.6rem 1rem !important;
        font-size: 0.95rem !important;
        color: #212121 !important;
        background: #fafafa !important;
    }

    .stTextInput input:focus {
        border-color: #3f51b5 !important;
        box-shadow: 0 0 0 3px rgba(63,81,181,0.1) !important;
    }

    .stTextInput label {
        color: #424242 !important;
        font-size: 0.85rem !important;
        font-weight: 500 !important;
    }

    .stButton > button {
        background: linear-gradient(135deg, #3f51b5, #5c6bc0) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.7rem 1rem !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        width: 100% !important;
        transition: all 0.3s !important;
        box-shadow: 0 4px 15px rgba(63,81,181,0.3) !important;
    }

    .stButton > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 20px rgba(63,81,181,0.4) !important;
    }

    .guest-btn > button {
        background: white !important;
        color: #3f51b5 !important;
        border: 1.5px solid #3f51b5 !important;
        box-shadow: none !important;
    }

    .divider {
        text-align: center;
        color: #9e9e9e;
        font-size: 0.85rem;
        margin: 0.75rem 0;
        position: relative;
    }

    .divider::before, .divider::after {
        content: '';
        position: absolute;
        top: 50%;
        width: 42%;
        height: 1px;
        background: #e0e0e0;
    }

    .divider::before { left: 0; }
    .divider::after { right: 0; }

    .stSuccess, .stError {
        border-radius: 10px !important;
        font-size: 0.85rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Centered layout
    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown("""
        <div class="login-logo">
            <div style="font-size:3rem;">🎓</div>
            <h1>NIST Helpdesk</h1>
            <p>AI-powered support, instantly</p>
        </div>
        """, unsafe_allow_html=True)

        tab = st.radio("", ["Login", "Sign Up"], horizontal=True, label_visibility="collapsed")

        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

        if tab == "Login":
            email = st.text_input("Email", placeholder="you@example.com", key="login_email")
            password = st.text_input("Password", type="password", placeholder="••••••••", key="login_pass")
            st.markdown("<div style='height:0.25rem'></div>", unsafe_allow_html=True)

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
                    except:
                        st.error("❌ Cannot connect to server")

            st.markdown("<div class='divider'>or</div>", unsafe_allow_html=True)
            st.markdown("<div class='guest-btn'>", unsafe_allow_html=True)
            if st.button("Continue as Guest", key="btn_guest"):
                st.session_state.user = {"id": "guest", "name": "Guest", "role": "guest"}
                st.session_state.screen = "chat"
                st.session_state.messages = []
                st.session_state.session_id = None
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        else:
            name = st.text_input("Full Name", placeholder="Your name", key="signup_name")
            email = st.text_input("Email", placeholder="you@example.com", key="signup_email")
            password = st.text_input("Password", type="password", placeholder="Min 6 characters", key="signup_pass")
            st.markdown("<div style='height:0.25rem'></div>", unsafe_allow_html=True)

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
                    except:
                        st.error("❌ Cannot connect to server")


def show():
    show_login()
