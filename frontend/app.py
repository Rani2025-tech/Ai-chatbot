import streamlit as st
import os

# When deployed as single service, backend runs on localhost:8000
if not os.getenv("API_URL"):
    os.environ["API_URL"] = "http://localhost:8000/api"

st.set_page_config(
    page_title="NIST AI Helpdesk",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="auto"
)

import sys
sys.path.insert(0, os.path.dirname(__file__))
import login
import dashboard
import chat
import admin

# Inject font preconnect + Inter into <head>
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)

# Load shared CSS once
css_path = os.path.join(os.path.dirname(__file__), "style.css")
with open(css_path) as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

if "screen" not in st.session_state:
    st.session_state.screen = "login"

screen = st.session_state.screen
HIDE_SIDEBAR = "<style>section[data-testid='stSidebar']{display:none !important;}</style>"

LOGIN_STYLES = """
<style>
.stApp { background: var(--color-bg-page) !important; }
.block-container { padding: 1.5rem 1rem !important; max-width: 480px !important; margin: 0 auto !important; }
</style>
"""

if screen == "login":
    st.markdown(HIDE_SIDEBAR, unsafe_allow_html=True)
    st.markdown(LOGIN_STYLES, unsafe_allow_html=True)
    login.show()
elif screen == "dashboard":
    st.markdown(HIDE_SIDEBAR, unsafe_allow_html=True)
    dashboard.show()
elif screen == "chat":
    chat.show()
elif screen == "admin":
    st.markdown(HIDE_SIDEBAR, unsafe_allow_html=True)
    admin.show()
