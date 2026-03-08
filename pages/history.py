"""
Past Vibes Page
Revisit your screening sessions with full candidate details.
"""
import streamlit as st
from datetime import datetime

from utils.history_store import load_all_sessions, load_session, delete_session
from utils.exporter import export_to_excel, export_to_csv

# ── CSS ─────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .session-card {
        background: linear-gradient(145deg, #1e1e2f, #2a2a40);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 14px; padding: 1.2rem 1.5rem;
        margin-bottom: 0.8rem; transition: transform 0.15s;
    }
    .session-card:hover { transform: translateY(-1px); }
    .session-title {
        font-size: 1.1rem; font-weight: 600;
        background: linear-gradient(90deg, #667eea, #a78bfa);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .session-meta { color: #888; font-size: 0.85rem; margin-top: 0.3rem; }
    .session-stats { color: #aaa; font-size: 0.9rem; margin-top: 0.5rem; }
    .stag {
        display: inline-block; padding: 0.2rem 0.6rem; margin: 0.12rem;
        border-radius: 6px; font-size: 0.78rem; font-weight: 500;
    }
    .stag-green { background: #22c55e18; color: #22c55e; border: 1px solid #22c55e44; }
    .stag-red { background: #ef444418; color: #ef4444; border: 1px solid #ef444444; }
    .stag-amber { background: #f59e0b18; color: #f59e0b; border: 1px solid #f59e0b44; }
    .stag-blue { background: #3b82f618; color: #3b82f6; border: 1px solid #3b82f644; }
</style>
""", unsafe_allow_html=True)

st.markdown("# 📜 Past Vibes")
st.caption("Every vibe check you've ever run, saved right here on your machine")

sessions = load_all_sessions()
if not sessions:
    st.info("✨ No vibes checked yet! Head to **Vibe Screen Resumes** to start.")
    st.stop()

st.markdown(f"**{len(sessions)}** session(s) found")
st.markdown("---")

for s in sessions:
    sid = s["session_id"]
    ts = s["timestamp"]
    title = s["jd_title"]
    total = s["total_resumes"]
    qualified = s["qualified_count"]
    thresh = s["threshold"]

    try:
        dt = datetime.fromisoformat(ts)
        time_str = dt.strftime("%b %d, %Y at %I:%M %p")
    except ValueError:
        time_str = ts

    st.markdown(f"""
    <div class="session-card">
        <div class="session-title">{title}</div>
        <div class="session-meta">{time_str} &nbsp;|&nbsp; Threshold: {thresh}%</div>
        <div class="session-stats">{total} resumes &rarr; <strong>{qualified}</strong> qualified</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([5, 1])
    with col1:
        if st.button("✨ View Details", key=f"view_{sid}", use_container_width=True, type="primary"):
            st.session_state[f"expand_{sid}"] = not st.session_state.get(f"expand_{sid}", False)
    with col2:
        if st.button("🗑️", key=f"del_{sid}", help="Delete session"):
            delete_session(sid)
            st.rerun()

    if st.session_state.get(f"expand_{sid}", False):
        full_data = load_session(sid)
        if full_data:
            candidates = full_data.get("candidates", [])
            sorted_cands = sorted(candidates, key=lambda x: x.get("match_score", 0), reverse=True)

            if sorted_cands:
                q_count = sum(1 for c in sorted_cands if c.get("match_score", 0) >= thresh)
                st.markdown(f"**{q_count}** qualified &nbsp;|&nbsp; **{len(sorted_cands) - q_count}** below threshold")

                # Downloads
                qualified_list = [c for c in sorted_cands if c.get("match_score", 0) >= thresh]
                if qualified_list:
                    dl1, dl2, dl3 = st.columns([2, 2, 6])
                    with dl1:
                        st.download_button("📥 Excel", export_to_excel(qualified_list),
                            f"shortlist_{sid}.xlsx",
                            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            key=f"xl_{sid}")
                    with dl2:
                        st.download_button("📥 CSV", export_to_csv(qualified_list),
                            f"shortlist_{sid}.csv", "text/csv", key=f"csv_{sid}")

                # Candidate cards
                for rank, c in enumerate(sorted_cands, 1):
                    name = c.get("name") or c.get("source_file", "Unknown")
                    score = c.get("match_score", 0)
                    is_q = score >= thresh
                    color = "#22c55e" if score >= 70 else "#eab308" if score >= thresh else "#ef4444"
                    matched = c.get("matched_skills", [])
                    missing = c.get("missing_skills", [])
                    explanation = c.get("explanation", {})
                    risks = c.get("risks", [])
                    profile = c.get("resume_profile", {})
                    composite = c.get("composite", {})

                    with st.container(border=True):
                        hc1, hc2 = st.columns([4, 1])
                        with hc1:
                            status_icon = "✅" if is_q else "❌"
                            st.markdown(f"### {status_icon} #{rank} {name}")
                        with hc2:
                            st.markdown(f"<div style='text-align:right;padding-top:0.5rem;'>"
                                f"<span style='background:{color}33;color:{color};"
                                f"padding:0.3rem 0.8rem;border-radius:999px;font-weight:700;"
                                f"font-size:1.1rem;'>{score:.1f}%</span></div>",
                                unsafe_allow_html=True)

                        # Score bar
                        bw = max(2, min(100, score))
                        st.markdown(f"<div style='width:100%;height:5px;background:rgba(255,255,255,0.06);"
                            f"border-radius:3px;margin-bottom:0.5rem;'>"
                            f"<div style='width:{bw}%;height:5px;border-radius:3px;"
                            f"background:linear-gradient(90deg,#667eea,{color});'></div></div>",
                            unsafe_allow_html=True)

                        # Score breakdown (if available)
                        if composite:
                            mc1, mc2, mc3, mc4 = st.columns(4)
                            with mc1:
                                st.metric("Semantic", f"{composite.get('semantic_score', 0):.0f}%")
                            with mc2:
                                st.metric("Skills", f"{composite.get('skill_score', 0):.0f}%")
                            with mc3:
                                st.metric("Experience", f"{composite.get('experience_score', 0):.0f}%")
                            with mc4:
                                st.metric("Seniority", f"{composite.get('seniority_score', 0):.0f}%")

                        # Contact
                        cc1, cc2, cc3, cc4 = st.columns(4)
                        with cc1:
                            email = c.get("email", "")
                            st.markdown(f"📧 [{email}](mailto:{email})" if email else "📧 —")
                        with cc2:
                            st.markdown(f"📱 {c.get('phone', '') or '—'}")
                        with cc3:
                            st.markdown(f"📍 {c.get('location', '') or '—'}")
                        with cc4:
                            ln = c.get("linkedin", "")
                            st.markdown(f"💼 [LinkedIn]({ln})" if ln else "💼 —")

                        # AI Summary
                        summary = explanation.get("summary", "")
                        if summary:
                            st.info(f"🤖 **AI Summary:** {summary}")

                        # Strengths & Gaps
                        sg1, sg2 = st.columns(2)
                        with sg1:
                            st.markdown("**✅ Strengths**")
                            for s_item in explanation.get("strengths", []):
                                st.markdown(f"- {s_item}")
                        with sg2:
                            st.markdown("**⚠️ Gaps**")
                            gaps = explanation.get("gaps", [])
                            if gaps:
                                for g in gaps:
                                    st.markdown(f"- {g}")
                            else:
                                st.markdown("None — strong fit!")

                        # Risk signals
                        if risks:
                            st.markdown("**🚨 Risk Signals**")
                            for r in risks:
                                cls = {"high": "stag-red", "medium": "stag-amber", "low": "stag-blue"}.get(r["severity"], "stag-blue")
                                st.markdown(f"<span class='stag {cls}'>{r['severity'].upper()}</span> "
                                    f"**{r['signal']}** — {r['detail']}", unsafe_allow_html=True)

                        # Skills
                        with st.expander(f"🔬 Skills: {len(matched)} matched, {len(missing)} missing"):
                            sk1, sk2 = st.columns(2)
                            with sk1:
                                st.markdown("**Matched**")
                                if matched:
                                    st.markdown(" ".join(f"<span class='stag stag-green'>{s}</span>" for s in matched),
                                        unsafe_allow_html=True)
                                else:
                                    st.caption("None")
                            with sk2:
                                st.markdown("**Missing**")
                                if missing:
                                    st.markdown(" ".join(f"<span class='stag stag-red'>{s}</span>" for s in missing),
                                        unsafe_allow_html=True)
                                else:
                                    st.markdown("🎉 All matched!")

            failed = full_data.get("failed_files", [])
            if failed:
                with st.expander(f"⚠️ {len(failed)} failed"):
                    for f in failed:
                        st.caption(f"- {f['file']}: {f['reason']}")

    st.markdown("---")
