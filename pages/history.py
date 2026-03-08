"""
Past Vibes Page
Revisit your screening sessions and relive the vibe checks.
"""
import streamlit as st
import pandas as pd
from datetime import datetime

from utils.history_store import load_all_sessions, load_session, delete_session
from utils.exporter import export_to_excel, export_to_csv

# ── CSS ─────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .session-card {
        background: linear-gradient(145deg, #1e1e2f, #2a2a40);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 14px;
        padding: 1.2rem 1.5rem;
        margin-bottom: 0.8rem;
        transition: transform 0.15s;
    }
    .session-card:hover { transform: translateY(-1px); }
    .session-title {
        font-size: 1.1rem; font-weight: 600;
        background: linear-gradient(90deg, #667eea, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .session-meta { color: #888; font-size: 0.85rem; margin-top: 0.3rem; }
    .session-stats { color: #aaa; font-size: 0.9rem; margin-top: 0.5rem; }

    .skill-tag {
        display: inline-block; padding: 0.15rem 0.5rem; margin: 0.1rem;
        border-radius: 6px; font-size: 0.75rem; font-weight: 500;
    }
    .skill-matched { background: #22c55e22; color: #22c55e; border: 1px solid #22c55e44; }
    .skill-missing { background: #ef444422; color: #ef4444; border: 1px solid #ef444444; }
</style>
""", unsafe_allow_html=True)

# ── Header ──────────────────────────────────────────────────────────────────────
st.markdown("# 📜 Past Vibes")
st.caption("Every vibe check you've ever run, saved right here on your machine")

# ── Load sessions ───────────────────────────────────────────────────────────────
sessions = load_all_sessions()

if not sessions:
    st.info("✨ No vibes checked yet! Head to **Vibe Check** to start your first screening.")
    st.stop()

st.markdown(f"**{len(sessions)}** session(s) found")
st.markdown("---")

# ── Session List ────────────────────────────────────────────────────────────────
for s in sessions:
    sid = s["session_id"]
    ts = s["timestamp"]
    title = s["jd_title"]
    total = s["total_resumes"]
    qualified = s["qualified_count"]
    thresh = s["threshold"]

    # Format timestamp
    try:
        dt = datetime.fromisoformat(ts)
        time_str = dt.strftime("%b %d, %Y at %I:%M %p")
    except ValueError:
        time_str = ts

    # Session card
    st.markdown(f"""
    <div class="session-card">
        <div class="session-title">{title}</div>
        <div class="session-meta">{time_str} &nbsp;|&nbsp; Threshold: {thresh}%</div>
        <div class="session-stats">
            {total} resumes &rarr; <strong>{qualified}</strong> qualified
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([2, 2, 1])

    with col1:
        if st.button(f"📋 View Details", key=f"view_{sid}", use_container_width=True):
            st.session_state[f"expand_{sid}"] = not st.session_state.get(f"expand_{sid}", False)

    with col2:
        full_data = load_session(sid)
        if full_data:
            candidates = full_data.get("candidates", [])
            qualified_candidates = [c for c in candidates if c.get("match_score", 0) >= thresh]
            if qualified_candidates:
                excel = export_to_excel(qualified_candidates)
                st.download_button(
                    "📥 Excel",
                    data=excel,
                    file_name=f"shortlist_{sid}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key=f"dl_{sid}",
                    use_container_width=True,
                )

    with col3:
        if st.button("🗑️", key=f"del_{sid}", help="Delete this session"):
            delete_session(sid)
            st.rerun()

    # Expandable details
    if st.session_state.get(f"expand_{sid}", False):
        full_data = load_session(sid)
        if full_data:
            candidates = full_data.get("candidates", [])
            if candidates:
                df = pd.DataFrame([{
                    "Name": c.get("name") or "N/A",
                    "Email": c.get("email") or "N/A",
                    "Score (%)": c.get("match_score", 0),
                    "Matched": len(c.get("matched_skills", [])),
                    "Missing": len(c.get("missing_skills", [])),
                    "Status": "✅" if c.get("match_score", 0) >= thresh else "❌",
                } for c in sorted(candidates, key=lambda x: x["match_score"], reverse=True)])

                st.dataframe(df, use_container_width=True, hide_index=True)

                # Skill details per candidate
                for c in sorted(candidates, key=lambda x: x["match_score"], reverse=True):
                    name = c.get("name") or c.get("source_file", "Unknown")
                    matched = c.get("matched_skills", [])
                    missing = c.get("missing_skills", [])
                    if matched or missing:
                        with st.expander(f"{name} — skills"):
                            c1, c2 = st.columns(2)
                            with c1:
                                if matched:
                                    html = " ".join(f"<span class='skill-tag skill-matched'>{s}</span>" for s in matched)
                                    st.markdown(html, unsafe_allow_html=True)
                            with c2:
                                if missing:
                                    html = " ".join(f"<span class='skill-tag skill-missing'>{s}</span>" for s in missing)
                                    st.markdown(html, unsafe_allow_html=True)

            # Failed files
            failed = full_data.get("failed_files", [])
            if failed:
                st.warning(f"{len(failed)} file(s) failed to parse")
                for f in failed:
                    st.caption(f"- {f['file']}: {f['reason']}")

    st.markdown("---")
