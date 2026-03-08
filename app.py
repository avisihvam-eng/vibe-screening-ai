"""
Vibe Screening AI — Main App (Multi-Page)
"""
import streamlit as st

# ── Page Config ─────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Vibe Screening AI",
    page_icon="✨",
    layout="wide",
)

# ── Navigation ──────────────────────────────────────────────────────────────────
screen_page = st.Page("pages/screen.py", title="Vibe Screen Resumes", icon="✨", default=True)
history_page = st.Page("pages/history.py", title="Past Vibes", icon="📜")
dashboard_page = st.Page("pages/dashboard.py", title="Vibe Dashboard", icon="📊")

nav = st.navigation([screen_page, history_page, dashboard_page])
nav.run()
