import streamlit as st
import requests
import os

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000/api")

def show():
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

        if st.button("Login", key="btn_login", type="primary"):
            if not email or not password:
                st.error("Please fill in all fields")
            else:
                try:
                    res = requests.post(
                        f"{API_URL}/auth/login",
                        json={"email": email, "password": password},
                        timeout=5
                    )
                    if res.status_code == 200:
                        user = res.json()
                        st.session_state.user = user
                        st.session_state.token = user.get("token", "")
                        st.session_state.screen = "admin" if user["role"] == "admin" else "dashboard"
                        st.rerun()
                    else:
                        detail = res.json().get("detail", "Login failed")
                        st.error(f"❌ {detail}")
                except requests.exceptions.ConnectionError:
                    st.error("❌ Cannot connect to backend. Make sure FastAPI is running on port 8000.")
                except requests.exceptions.Timeout:
                    st.error("❌ Server took too long to respond. Is the backend running?")
                except Exception as e:
                    st.error(f"❌ Error: {e}")

        st.markdown("<div class='divider'>or</div>", unsafe_allow_html=True)

        if st.button("Continue as Guest", key="btn_guest"):
            st.session_state.user = {"id": "guest", "name": "Guest", "role": "guest"}
            st.session_state.token = ""
            st.session_state.screen = "chat"
            st.session_state.messages = []
            st.session_state.session_id = None
            st.rerun()

    else:
        name = st.text_input("Full Name", placeholder="Your full name", key="signup_name")
        email = st.text_input("Email address", placeholder="you@example.com", key="signup_email")
        password = st.text_input("Password", type="password", placeholder="Min 6 characters", key="signup_pass")
        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

        if st.button("Create Account", key="btn_signup", type="primary"):
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
