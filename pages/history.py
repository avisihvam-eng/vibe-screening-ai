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

    .candidate-card {
        background: linear-gradient(145deg, #16162a, #1e1e38);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        transition: transform 0.15s, box-shadow 0.15s;
    }
    .candidate-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.3);
    }
    .candidate-card.qualified {
        border-left: 4px solid #22c55e;
    }
    .candidate-card.not-qualified {
        border-left: 4px solid #ef4444;
        opacity: 0.75;
    }

    .candidate-name {
        font-size: 1.3rem; font-weight: 700;
        background: linear-gradient(90deg, #f0f0f0, #d0d0f0);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.3rem;
    }

    .candidate-score {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 999px;
        font-size: 0.85rem;
        font-weight: 700;
        margin-left: 0.5rem;
    }
    .score-high { background: #22c55e33; color: #22c55e; }
    .score-mid { background: #eab30833; color: #eab308; }
    .score-low { background: #ef444433; color: #ef4444; }

    .contact-row {
        display: flex; flex-wrap: wrap; gap: 1rem;
        margin: 0.8rem 0;
        padding: 0.7rem 1rem;
        background: rgba(255,255,255,0.03);
        border-radius: 10px;
    }
    .contact-item {
        display: flex; align-items: center; gap: 0.4rem;
        font-size: 0.85rem; color: #bbb;
    }
    .contact-item a { color: #667eea; text-decoration: none; }
    .contact-item a:hover { text-decoration: underline; }
    .contact-icon { font-size: 1rem; }

    .skill-section {
        margin-top: 0.8rem;
        padding: 0.8rem 1rem;
        background: rgba(255,255,255,0.02);
        border-radius: 10px;
    }
    .skill-section-title {
        font-size: 0.8rem; font-weight: 600;
        text-transform: uppercase; letter-spacing: 1px;
        margin-bottom: 0.5rem;
    }
    .skill-title-match { color: #22c55e; }
    .skill-title-miss { color: #ef4444; }

    .skill-tag {
        display: inline-block; padding: 0.2rem 0.6rem; margin: 0.15rem;
        border-radius: 6px; font-size: 0.78rem; font-weight: 500;
    }
    .skill-matched { background: #22c55e18; color: #22c55e; border: 1px solid #22c55e44; }
    .skill-missing { background: #ef444418; color: #ef4444; border: 1px solid #ef444444; }

    .match-bar-bg {
        width: 100%; height: 6px; background: rgba(255,255,255,0.06);
        border-radius: 3px; margin-top: 0.5rem;
    }
    .match-bar-fill {
        height: 6px; border-radius: 3px;
        background: linear-gradient(90deg, #667eea, #22c55e);
    }

    .file-badge {
        display: inline-block; padding: 0.15rem 0.5rem;
        background: rgba(102,126,234,0.15); color: #667eea;
        border-radius: 6px; font-size: 0.75rem;
    }
</style>
""", unsafe_allow_html=True)

# ── Header ──────────────────────────────────────────────────────────────────────
st.markdown("# 📜 Past Vibes")
st.caption("Every vibe check you've ever run, saved right here on your machine")

# ── Load sessions ───────────────────────────────────────────────────────────────
sessions = load_all_sessions()

if not sessions:
    st.info("✨ No vibes checked yet! Head to **Vibe Screen Resumes** to start your first screening.")
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

    col1, col2 = st.columns([5, 1])

    with col1:
        if st.button("✨ View Details", key=f"view_{sid}", use_container_width=True, type="primary"):
            st.session_state[f"expand_{sid}"] = not st.session_state.get(f"expand_{sid}", False)

    with col2:
        if st.button("🗑️", key=f"del_{sid}", help="Delete this session"):
            delete_session(sid)
            st.rerun()

    # ── EXPANDED DETAILS ────────────────────────────────────────────────────
    if st.session_state.get(f"expand_{sid}", False):
        full_data = load_session(sid)
        if full_data:
            candidates = full_data.get("candidates", [])
            sorted_candidates = sorted(candidates, key=lambda x: x.get("match_score", 0), reverse=True)

            if sorted_candidates:
                # Quick stats bar
                q_count = sum(1 for c in sorted_candidates if c.get("match_score", 0) >= thresh)
                st.markdown(f"**{q_count}** passed the vibe check &nbsp;|&nbsp; **{len(sorted_candidates) - q_count}** didn't make it")

                # Download row (compact, not the focus)
                dl1, dl2, dl3 = st.columns([2, 2, 6])
                qualified_list = [c for c in sorted_candidates if c.get("match_score", 0) >= thresh]
                if qualified_list:
                    with dl1:
                        st.download_button(
                            "📥 Excel", data=export_to_excel(qualified_list),
                            file_name=f"shortlist_{sid}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            key=f"dl_xl_{sid}",
                        )
                    with dl2:
                        st.download_button(
                            "📥 CSV", data=export_to_csv(qualified_list),
                            file_name=f"shortlist_{sid}.csv",
                            mime="text/csv",
                            key=f"dl_csv_{sid}",
                        )

                st.markdown("")

                # ── Candidate Profile Cards ─────────────────────────────────
                for c in sorted_candidates:
                    name = c.get("name") or "Unknown Candidate"
                    email = c.get("email") or ""
                    phone = c.get("phone") or ""
                    location = c.get("location") or ""
                    linkedin = c.get("linkedin") or ""
                    score = c.get("match_score", 0)
                    matched = c.get("matched_skills", [])
                    missing = c.get("missing_skills", [])
                    source = c.get("source_file", "")
                    is_qualified = score >= thresh

                    # Score badge color
                    if score >= 70:
                        score_class = "score-high"
                    elif score >= thresh:
                        score_class = "score-mid"
                    else:
                        score_class = "score-low"

                    card_class = "qualified" if is_qualified else "not-qualified"
                    status_emoji = "✅" if is_qualified else "❌"

                    # Build contact items
                    contact_items = []
                    if email:
                        contact_items.append(
                            f'<div class="contact-item"><span class="contact-icon">📧</span>'
                            f'<a href="mailto:{email}">{email}</a></div>'
                        )
                    if phone:
                        contact_items.append(
                            f'<div class="contact-item"><span class="contact-icon">📱</span>{phone}</div>'
                        )
                    if location:
                        contact_items.append(
                            f'<div class="contact-item"><span class="contact-icon">📍</span>{location}</div>'
                        )
                    if linkedin:
                        ln_url = linkedin if linkedin.startswith("http") else f"https://{linkedin}"
                        contact_items.append(
                            f'<div class="contact-item"><span class="contact-icon">💼</span>'
                            f'<a href="{ln_url}" target="_blank">{linkedin}</a></div>'
                        )
                    if source:
                        contact_items.append(
                            f'<div class="contact-item"><span class="file-badge">📄 {source}</span></div>'
                        )

                    contact_html = "\n".join(contact_items) if contact_items else '<div class="contact-item" style="color:#666">No contact info extracted</div>'

                    # Build skill tags
                    matched_html = " ".join(
                        f'<span class="skill-tag skill-matched">{s}</span>' for s in matched
                    ) if matched else '<span style="color:#666; font-size:0.8rem">None detected</span>'

                    missing_html = " ".join(
                        f'<span class="skill-tag skill-missing">{s}</span>' for s in missing
                    ) if missing else '<span style="color:#22c55e; font-size:0.8rem">All skills matched! 🎉</span>'

                    # Match bar width
                    bar_width = max(2, min(100, score))

                    # Render the card
                    st.markdown(f"""
                    <div class="candidate-card {card_class}">
                        <div style="display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap;">
                            <div>
                                <span class="candidate-name">{status_emoji} {name}</span>
                                <span class="candidate-score {score_class}">{score:.1f}%</span>
                            </div>
                            <div style="color:#888; font-size:0.8rem;">
                                {len(matched)} skills matched &nbsp;|&nbsp; {len(missing)} missing
                            </div>
                        </div>

                        <div class="match-bar-bg">
                            <div class="match-bar-fill" style="width:{bar_width}%"></div>
                        </div>

                        <div class="contact-row">
                            {contact_html}
                        </div>

                        <div style="display:flex; gap:0.8rem; flex-wrap:wrap;">
                            <div class="skill-section" style="flex:1; min-width:200px;">
                                <div class="skill-section-title skill-title-match">✅ Matched Skills ({len(matched)})</div>
                                {matched_html}
                            </div>
                            <div class="skill-section" style="flex:1; min-width:200px;">
                                <div class="skill-section-title skill-title-miss">❌ Missing Skills ({len(missing)})</div>
                                {missing_html}
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

            # Failed files
            failed = full_data.get("failed_files", [])
            if failed:
                with st.expander(f"⚠️ {len(failed)} file(s) failed to parse"):
                    for f in failed:
                        st.caption(f"- {f['file']}: {f['reason']}")

    st.markdown("---")
