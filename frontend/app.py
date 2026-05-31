import streamlit as st

st.set_page_config(
    page_title="NIST AI Helpdesk",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import login
import dashboard
import chat
import admin

if "screen" not in st.session_state:
    st.session_state.screen = "login"

screen = st.session_state.screen

if screen == "login":
    login.show()
elif screen == "dashboard":
    dashboard.show()
elif screen == "chat":
    chat.show()
elif screen == "admin":
    admin.show()
