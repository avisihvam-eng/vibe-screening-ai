"""
Dashboard Page
Aggregate analytics across all screening sessions.
"""
import streamlit as st
import pandas as pd
from collections import Counter
from datetime import datetime

from utils.history_store import load_all_sessions, load_session

# ── CSS ─────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .dash-card {
        background: linear-gradient(145deg, #1e1e2f, #2a2a40);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 14px;
        padding: 1.5rem;
        text-align: center;
    }
    .dash-value {
        font-size: 2.8rem; font-weight: 800;
        background: linear-gradient(90deg, #667eea, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .dash-label {
        font-size: 0.85rem; color: #aaa; margin-top: 0.3rem;
        text-transform: uppercase; letter-spacing: 1px;
    }
</style>
""", unsafe_allow_html=True)

# ── Header ──────────────────────────────────────────────────────────────────────
st.markdown("# 📊 Dashboard")
st.caption("Aggregate insights across all screening sessions")

# ── Load data ───────────────────────────────────────────────────────────────────
sessions = load_all_sessions()

if not sessions:
    st.info("No data yet. Run a screening from the **Screen Resumes** page to see analytics here.")
    st.stop()

# ── Compute aggregate stats ─────────────────────────────────────────────────────
total_sessions = len(sessions)
total_resumes = sum(s["total_resumes"] for s in sessions)
total_qualified = sum(s["qualified_count"] for s in sessions)
avg_qual_rate = (total_qualified / total_resumes * 100) if total_resumes > 0 else 0

# ── Top Cards ───────────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""
    <div class="dash-card">
        <div class="dash-value">{total_sessions}</div>
        <div class="dash-label">Sessions</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="dash-card">
        <div class="dash-value">{total_resumes}</div>
        <div class="dash-label">Resumes Screened</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="dash-card">
        <div class="dash-value">{total_qualified}</div>
        <div class="dash-label">Total Qualified</div>
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class="dash-card">
        <div class="dash-value">{avg_qual_rate:.0f}%</div>
        <div class="dash-label">Avg Pass Rate</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ── Sessions Over Time ──────────────────────────────────────────────────────────
st.markdown("### Sessions Over Time")

dates = []
for s in sessions:
    try:
        dt = datetime.fromisoformat(s["timestamp"])
        dates.append(dt.strftime("%Y-%m-%d"))
    except ValueError:
        pass

if dates:
    date_counts = Counter(dates)
    df_dates = pd.DataFrame(
        sorted(date_counts.items()),
        columns=["Date", "Sessions"],
    )
    df_dates["Date"] = pd.to_datetime(df_dates["Date"])
    st.bar_chart(df_dates.set_index("Date"), color="#667eea")
else:
    st.caption("Not enough data to show trends yet.")

# ── Session Summary Table ───────────────────────────────────────────────────────
st.markdown("### All Sessions")

df_sessions = pd.DataFrame([{
    "Date": s["timestamp"][:10],
    "JD Title": s["jd_title"][:50],
    "Threshold": f"{s['threshold']}%",
    "Resumes": s["total_resumes"],
    "Qualified": s["qualified_count"],
    "Pass Rate": f"{s['qualified_count'] / s['total_resumes'] * 100:.0f}%" if s["total_resumes"] > 0 else "0%",
} for s in sessions])

st.dataframe(df_sessions, use_container_width=True, hide_index=True)

# ── Most Common Missing Skills ──────────────────────────────────────────────────
st.markdown("### 🔴 Most Common Missing Skills")
st.caption("Skills that candidates lack most often across all sessions")

missing_counter: Counter = Counter()

for s in sessions:
    full = load_session(s["session_id"])
    if not full:
        continue
    for c in full.get("candidates", []):
        for skill in c.get("missing_skills", []):
            missing_counter[skill] += 1

if missing_counter:
    top_missing = missing_counter.most_common(15)
    df_skills = pd.DataFrame(top_missing, columns=["Skill", "Times Missing"])
    st.bar_chart(df_skills.set_index("Skill"), color="#ef4444")
else:
    st.caption("No skill data available yet.")

# ── Top Candidates Across Sessions ──────────────────────────────────────────────
st.markdown("### 🏆 Top Candidates (All Time)")
st.caption("Highest scoring candidates across all sessions")

all_candidates = []
for s in sessions:
    full = load_session(s["session_id"])
    if not full:
        continue
    for c in full.get("candidates", []):
        all_candidates.append({
            "Name": c.get("name") or "N/A",
            "Email": c.get("email") or "N/A",
            "Score (%)": c.get("match_score", 0),
            "Session": full.get("jd_title", "")[:40],
            "Date": full.get("timestamp", "")[:10],
        })

if all_candidates:
    # Deduplicate by email, keep highest score
    seen = {}
    for c in all_candidates:
        email = c["Email"].lower()
        if email not in seen or c["Score (%)"] > seen[email]["Score (%)"]:
            seen[email] = c
    top = sorted(seen.values(), key=lambda x: x["Score (%)"], reverse=True)[:20]
    st.dataframe(pd.DataFrame(top), use_container_width=True, hide_index=True)
else:
    st.caption("No candidate data available yet.")
