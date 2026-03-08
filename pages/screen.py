"""
Vibe Screen Resumes Page
The main screening workflow — now with JD intelligence, composite scoring,
explainable AI, and risk signals.
"""
import streamlit as st
import pandas as pd
import time

from utils.resume_parser import extract_text
from utils.info_extractor import extract_candidate_info
from utils.chunker import chunk_text
from utils.embedder import get_embeddings, load_model
from utils.scorer import score_candidate
from utils.exporter import export_to_excel, export_to_csv
from utils.skill_matcher import extract_skills, match_skills
from utils.history_store import save_session
from utils.jd_analyzer import analyze_jd
from utils.resume_analyzer import analyze_resume
from utils.match_engine import compute_composite_score, generate_explanation
from utils.risk_detector import detect_risks

# ── Custom CSS ──────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main .block-container { padding-top: 1.5rem; }
    .app-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem 2.5rem; border-radius: 16px; margin-bottom: 1.5rem; color: white;
    }
    .app-header h1 { margin: 0; font-size: 2.2rem; font-weight: 700; }
    .app-header p { margin: 0.5rem 0 0 0; opacity: 0.9; font-size: 1.05rem; }

    .metric-row { display: flex; gap: 1rem; margin: 1.5rem 0; }
    .metric-card {
        flex: 1; background: linear-gradient(145deg, #1e1e2f, #2a2a40);
        border: 1px solid rgba(255,255,255,0.06); border-radius: 14px;
        padding: 1.2rem; text-align: center; transition: transform 0.2s;
    }
    .metric-card:hover { transform: translateY(-2px); }
    .metric-card .value {
        font-size: 2.2rem; font-weight: 800;
        background: linear-gradient(90deg, #667eea, #a78bfa);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .metric-card .label {
        font-size: 0.8rem; color: #aaa; margin-top: 0.2rem;
        text-transform: uppercase; letter-spacing: 1px;
    }
    .badge-success {
        display: inline-block; padding: 0.25rem 0.75rem;
        background: #22c55e22; color: #22c55e;
        border-radius: 999px; font-size: 0.8rem; font-weight: 600;
    }
    .stag {
        display: inline-block; padding: 0.2rem 0.6rem; margin: 0.12rem;
        border-radius: 6px; font-size: 0.78rem; font-weight: 500;
    }
    .stag-green { background: #22c55e18; color: #22c55e; border: 1px solid #22c55e44; }
    .stag-red { background: #ef444418; color: #ef4444; border: 1px solid #ef444444; }
    .stag-blue { background: #3b82f618; color: #3b82f6; border: 1px solid #3b82f644; }
    .stag-amber { background: #f59e0b18; color: #f59e0b; border: 1px solid #f59e0b44; }
    .stag-purple { background: #8b5cf618; color: #8b5cf6; border: 1px solid #8b5cf644; }
</style>
""", unsafe_allow_html=True)

# ── Header ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="app-header">
    <h1>✨ Vibe Screening AI</h1>
    <p>Drop a JD, throw in some resumes, and let the vibes decide who makes it. No gut feelings required.</p>
</div>
""", unsafe_allow_html=True)

# About section
with st.expander("🤖 What is this? (and what it's NOT)", expanded=False):
    st.markdown("""
**Vibe Screening AI** is your AI-powered recruiting sidekick that does the boring part of hiring.

#### ✨ What it IS:
- **A vibe-checker for resumes** — uses semantic AI to understand *meaning*, not just keywords
- **A skill gap detective** — shows which skills each candidate has vs. what's missing
- **An explainable ranker** — tells you *why* someone is a good match, not just a number
- **A risk spotter** — flags job hopping, career gaps, and skill inflation
- **Privacy-first** — everything runs on YOUR machine. No data leaves
- **100% free** — no API keys, no subscriptions

#### 🚫 What it is NOT:
- **Not a replacement for human judgment** — it ranks candidates, you make the call
- **Not a keyword matcher** — "ML Engineer" and "Machine Learning Developer" = same vibe
- **Not your ATS** — it's the bouncer at the club, not the club itself

> *"Traditional screening: Read 500 resumes, cry, hire someone random.*
> *Vibe screening: Let AI read 500 resumes, sip chai, hire someone good."*
    """)

# ── Sidebar ─────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ✨ Vibe Controls")
    threshold = st.slider("Vibe Threshold (%)", 0, 100, 40, 5,
        help="Only candidates scoring at or above this level make the cut.")
    st.markdown("---")
    st.markdown("### 🎯 How to Vibe Screen")
    st.markdown("""
1. Drop the **Job Description**
2. Throw in the **resumes** (PDF / DOCX / paste)
3. Hit **Check the Vibes**
4. See who passed ✨
    """)
    st.markdown("---")
    st.markdown(
        "<small style='color:#888'>Powered by <code>all-MiniLM-L6-v2</code> vibes<br>"
        "Zero APIs. Zero cost. Pure vibes.</small>",
        unsafe_allow_html=True,
    )

# ── Input Section ───────────────────────────────────────────────────────────────
col_jd, col_resumes = st.columns([1, 1], gap="large")

with col_jd:
    st.markdown("### 📝 Drop the JD")
    jd_text = st.text_area("JD", height=300,
        placeholder="e.g. We are looking for a Senior Python Developer with 5+ years of experience...",
        label_visibility="collapsed")

with col_resumes:
    st.markdown("### 📁 Throw in the Resumes")
    tab_upload, tab_paste = st.tabs(["📎 Upload Files", "📋 Paste Text"])
    with tab_upload:
        uploaded_files = st.file_uploader("Upload", type=["pdf", "docx"],
            accept_multiple_files=True, label_visibility="collapsed")
        if uploaded_files:
            st.markdown(f"<span class='badge-success'>✓ {len(uploaded_files)} file(s)</span>",
                unsafe_allow_html=True)
    with tab_paste:
        pasted_resumes_raw = st.text_area("Paste", height=250,
            placeholder="Paste resume text here.\nSeparate multiple resumes with ---",
            label_visibility="collapsed")
        parts = [p.strip() for p in pasted_resumes_raw.split("---") if p.strip()] if pasted_resumes_raw and pasted_resumes_raw.strip() else []
        if parts:
            st.markdown(f"<span class='badge-success'>✓ {len(parts)} pasted resume(s)</span>",
                unsafe_allow_html=True)

has_input = jd_text and (uploaded_files or parts)

st.markdown("---")
process_btn = st.button("✨ Check the Vibes", use_container_width=True, type="primary",
    disabled=not has_input)

# ── Processing ──────────────────────────────────────────────────────────────────
if process_btn and has_input:
    # Build unified resume list
    resume_items = []
    if uploaded_files:
        for uf in uploaded_files:
            resume_items.append({"type": "file", "name": uf.name, "file": uf})
    for idx, txt in enumerate(parts, 1):
        resume_items.append({"type": "pasted", "name": f"Pasted Resume #{idx}", "text": txt})

    total = len(resume_items)
    progress = st.progress(0, text="Initializing...")
    status = st.empty()

    # Step 1: Model
    status.info("⏳ Loading embedding model...")
    load_model()
    progress.progress(5, text="Model ready")

    # Step 2: Analyze JD
    status.info("⏳ Analyzing job description...")
    jd_analysis = analyze_jd(jd_text)
    jd_embedding = get_embeddings([jd_text])
    jd_skills = jd_analysis["all_skills"]
    progress.progress(10, text=f"JD analyzed — {len(jd_skills)} skills, "
        f"{len(jd_analysis['required_skills'])} required")

    # Step 3: Process resumes
    candidates = []
    failed_files = []

    for i, item in enumerate(resume_items):
        fname = item["name"]
        pct = 10 + int(70 * (i / total))
        progress.progress(pct, text=f"Analyzing {fname} ({i+1}/{total})")
        status.info(f"⏳ Analyzing **{fname}**...")

        # Parse text
        if item["type"] == "file":
            fb = item["file"].read()
            text, err = extract_text(fname, fb)
            if err:
                failed_files.append((fname, err))
                continue
        else:
            text = item["text"]

        # Extract info + deep analysis
        info = extract_candidate_info(text)
        resume_profile = analyze_resume(text)

        # Chunk & semantic score
        chunks = chunk_text(text)
        if not chunks:
            failed_files.append((fname, "Resume too short"))
            continue
        semantic_score = score_candidate(jd_embedding, chunks)

        # Skill match
        skill_result = match_skills(jd_skills, text)

        # Composite score
        composite = compute_composite_score(
            semantic_score=semantic_score,
            matched_skills=skill_result["matched"],
            missing_skills=skill_result["missing"],
            candidate_years=resume_profile["experience_years"],
            jd_exp_min=jd_analysis["experience_min"],
            jd_exp_max=jd_analysis["experience_max"],
            jd_seniority=jd_analysis["seniority"],
            candidate_skills_count=len(resume_profile["skills"]),
        )

        # Risk signals
        risks = detect_risks(resume_profile, jd_analysis)

        # Explanation
        explanation = generate_explanation(
            name=info["name"] or fname,
            matched_skills=skill_result["matched"],
            missing_skills=skill_result["missing"],
            candidate_years=resume_profile["experience_years"],
            jd_exp_min=jd_analysis["experience_min"],
            risks=risks,
            companies=resume_profile["companies"],
            education=resume_profile["education"],
            composite=composite,
        )

        candidate = {
            **info,
            "match_score": composite["composite_score"],
            "semantic_score": semantic_score,
            "composite": composite,
            "matched_skills": skill_result["matched"],
            "missing_skills": skill_result["missing"],
            "resume_profile": resume_profile,
            "risks": risks,
            "explanation": explanation,
            "notes": "",
            "source_file": fname,
        }
        candidates.append(candidate)

    # Rank
    progress.progress(85, text="Ranking candidates...")
    candidates.sort(key=lambda c: c["match_score"], reverse=True)
    qualified = [c for c in candidates if c["match_score"] >= threshold]

    # Save
    progress.progress(90, text="Saving session...")
    session_id = save_session(jd_text, threshold, candidates, failed_files)

    # Export
    progress.progress(95, text="Generating exports...")
    excel_bytes = export_to_excel(qualified) if qualified else None
    csv_str = export_to_csv(qualified) if qualified else None

    progress.progress(100, text="✅ Done!")
    status.empty()
    time.sleep(0.3)
    progress.empty()

    # ══════════════════════════════════════════════════════════════════════════
    # RESULTS
    # ══════════════════════════════════════════════════════════════════════════
    st.markdown("---")
    st.markdown("## ✨ Vibe Check Results")
    st.caption(f"Session `{session_id}` saved to history")

    # Metric cards
    st.markdown(f"""
    <div class="metric-row">
        <div class="metric-card"><div class="value">{total}</div><div class="label">Total Resumes</div></div>
        <div class="metric-card"><div class="value">{len(candidates)}</div><div class="label">Parsed OK</div></div>
        <div class="metric-card"><div class="value">{len(qualified)}</div><div class="label">Qualified (≥{threshold}%)</div></div>
        <div class="metric-card"><div class="value">{len(failed_files)}</div><div class="label">Failed</div></div>
    </div>
    """, unsafe_allow_html=True)

    # ── JD Intelligence Panel ───────────────────────────────────────────────
    with st.expander(f"🎯 JD Intelligence — {len(jd_analysis['required_skills'])} required, "
                     f"{len(jd_analysis['preferred_skills'])} preferred skills", expanded=True):
        jd_c1, jd_c2 = st.columns(2)
        with jd_c1:
            st.markdown("**Required Skills**")
            if jd_analysis["required_skills"]:
                tags = " ".join(f"<span class='stag stag-green'>{s}</span>" for s in jd_analysis["required_skills"])
                st.markdown(tags, unsafe_allow_html=True)
            else:
                st.caption("None explicitly marked")

            st.markdown("**Preferred Skills**")
            if jd_analysis["preferred_skills"]:
                tags = " ".join(f"<span class='stag stag-blue'>{s}</span>" for s in jd_analysis["preferred_skills"])
                st.markdown(tags, unsafe_allow_html=True)
            else:
                st.caption("None detected")

        with jd_c2:
            exp_str = "Not specified"
            if jd_analysis["experience_min"]:
                if jd_analysis["experience_max"]:
                    exp_str = f"{jd_analysis['experience_min']}–{jd_analysis['experience_max']} years"
                else:
                    exp_str = f"{jd_analysis['experience_min']}+ years"
            st.markdown(f"**Experience Level:** {exp_str}")
            st.markdown(f"**Seniority:** {(jd_analysis['seniority'] or 'Not specified').title()}")

            if jd_analysis["responsibilities"]:
                st.markdown("**Key Responsibilities**")
                for r in jd_analysis["responsibilities"][:5]:
                    st.caption(f"• {r[:100]}")

    # ── Candidate Ranking ───────────────────────────────────────────────────
    if qualified:
        st.markdown("### 🏆 Ranked Candidates")

        # Recruiter filters
        f_col1, f_col2 = st.columns(2)
        with f_col1:
            sort_by = st.selectbox("Sort by", ["Composite Score", "Semantic Score", "Skill Match", "Experience"],
                label_visibility="collapsed")
        with f_col2:
            min_score = st.slider("Min score filter", 0, 100, threshold, 5, label_visibility="collapsed")

        # Sort
        sort_key_map = {
            "Composite Score": lambda c: c["match_score"],
            "Semantic Score": lambda c: c.get("semantic_score", 0),
            "Skill Match": lambda c: len(c.get("matched_skills", [])),
            "Experience": lambda c: c.get("resume_profile", {}).get("experience_years") or 0,
        }
        display_candidates = [c for c in qualified if c["match_score"] >= min_score]
        display_candidates.sort(key=sort_key_map[sort_by], reverse=True)

        # Candidate cards
        for rank, c in enumerate(display_candidates, 1):
            name = c.get("name") or c.get("source_file", "Unknown")
            score = c["match_score"]
            composite = c.get("composite", {})
            explanation = c.get("explanation", {})
            risks = c.get("risks", [])
            profile = c.get("resume_profile", {})
            matched = c.get("matched_skills", [])
            missing = c.get("missing_skills", [])

            color = "#22c55e" if score >= 70 else "#eab308" if score >= threshold else "#ef4444"

            with st.container(border=True):
                # Header
                hc1, hc2 = st.columns([4, 1])
                with hc1:
                    st.markdown(f"### #{rank} {name}")
                with hc2:
                    st.markdown(f"<div style='text-align:right;padding-top:0.5rem;'>"
                        f"<span style='background:{color}33;color:{color};"
                        f"padding:0.3rem 0.8rem;border-radius:999px;font-weight:700;"
                        f"font-size:1.2rem;'>{score:.1f}%</span></div>",
                        unsafe_allow_html=True)

                # Score breakdown bar
                bar_w = max(2, min(100, score))
                st.markdown(f"<div style='width:100%;height:6px;background:rgba(255,255,255,0.06);"
                    f"border-radius:3px;margin-bottom:0.5rem;'>"
                    f"<div style='width:{bar_w}%;height:6px;border-radius:3px;"
                    f"background:linear-gradient(90deg,#667eea,{color});'></div></div>",
                    unsafe_allow_html=True)

                # Score breakdown chips
                sc1, sc2, sc3, sc4 = st.columns(4)
                with sc1:
                    st.metric("Semantic", f"{composite.get('semantic_score', 0):.0f}%")
                with sc2:
                    st.metric("Skills", f"{composite.get('skill_score', 0):.0f}%")
                with sc3:
                    st.metric("Experience", f"{composite.get('experience_score', 0):.0f}%")
                with sc4:
                    st.metric("Seniority", f"{composite.get('seniority_score', 0):.0f}%")

                # Contact info
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
                    if ln:
                        st.markdown(f"💼 [LinkedIn]({ln})")
                    else:
                        st.markdown("💼 —")

                # AI Summary
                summary = explanation.get("summary", "")
                if summary:
                    st.info(f"🤖 **AI Summary:** {summary}")

                # Strengths & Gaps
                sg1, sg2 = st.columns(2)
                with sg1:
                    st.markdown("**✅ Strengths**")
                    for s in explanation.get("strengths", []):
                        st.markdown(f"- {s}")
                with sg2:
                    st.markdown("**⚠️ Gaps**")
                    gaps = explanation.get("gaps", [])
                    if gaps:
                        for g in gaps:
                            st.markdown(f"- {g}")
                    else:
                        st.markdown("None — strong fit!")

                # Risk Signals
                if risks:
                    st.markdown("**🚨 Risk Signals**")
                    for r in risks:
                        sev_color = {"high": "stag-red", "medium": "stag-amber", "low": "stag-blue"}
                        cls = sev_color.get(r["severity"], "stag-blue")
                        st.markdown(
                            f"<span class='stag {cls}'>{r['severity'].upper()}</span> "
                            f"**{r['signal']}** — {r['detail']}",
                            unsafe_allow_html=True)

                # Skills breakdown
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

                # Profile details
                with st.expander("📋 Candidate Profile"):
                    pr1, pr2 = st.columns(2)
                    with pr1:
                        yrs = profile.get("experience_years")
                        st.markdown(f"**Experience:** {f'{yrs:.0f} years' if yrs else 'Not detected'}")
                        if profile.get("companies"):
                            st.markdown(f"**Companies:** {', '.join(profile['companies'][:5])}")
                        if profile.get("education"):
                            st.markdown(f"**Education:** {profile['education'][0]}")
                    with pr2:
                        if profile.get("projects"):
                            st.markdown("**Projects:**")
                            for p in profile["projects"][:4]:
                                st.caption(f"• {p[:80]}")
                        st.markdown(f"**Source:** `{c.get('source_file', '')}`")

        # Downloads
        st.markdown("---")
        dl1, dl2 = st.columns(2)
        with dl1:
            st.download_button("📥 Download Excel", data=excel_bytes,
                file_name="shortlisted_candidates.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True, type="primary")
        with dl2:
            st.download_button("📥 Download CSV", data=csv_str,
                file_name="shortlisted_candidates.csv", mime="text/csv",
                use_container_width=True)

    else:
        st.warning(f"No candidates matched at ≥ {threshold}%. Try lowering the threshold.")

    # Failed & below threshold
    if failed_files:
        with st.expander(f"⚠️ {len(failed_files)} file(s) failed"):
            for fn, reason in failed_files:
                st.markdown(f"- **{fn}**: {reason}")

    below = [c for c in candidates if c["match_score"] < threshold]
    if below:
        with st.expander(f"📉 {len(below)} candidate(s) below threshold"):
            for c in below:
                st.caption(f"- {c.get('name') or c.get('source_file', '')} — {c['match_score']:.1f}%")

elif not has_input:
    st.info("✨ Drop a JD and throw in some resumes to start the vibe check.")
