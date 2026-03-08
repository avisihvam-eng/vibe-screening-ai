"""
AutoResume Filter 40 — Main App (Multi-Page)
"""
import streamlit as st

# ── Page Config ─────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AutoResume Filter 40",
    page_icon="📄",
    layout="wide",
)

# ── Navigation ──────────────────────────────────────────────────────────────────
screen_page = st.Page("pages/screen.py", title="Screen Resumes", icon="🔍", default=True)
history_page = st.Page("pages/history.py", title="History", icon="📜")
dashboard_page = st.Page("pages/dashboard.py", title="Dashboard", icon="📊")

nav = st.navigation([screen_page, history_page, dashboard_page])
nav.run()
