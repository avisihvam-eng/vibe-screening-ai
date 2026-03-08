"""
Vibe Screen Resumes Page
The main screening workflow — now with a completely refactored 
modern SaaS frontend experience.
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

# ── Reset Callback ────────────────────────────────────────────────────────────
def do_reset():
    for key in list(st.session_state.keys()):
        del st.session_state[key]

# ── Custom CSS for SaaS Look ──────────────────────────────────────────────────
st.markdown("""
<style>
    .main .block-container { padding-top: 2rem; max-width: 1200px; }
    
    /* SaaS Header */
    .saas-header {
        text-align: center;
        padding: 3rem 2rem;
        background: linear-gradient(135deg, #1e1e2f 0%, #2a2a40 100%);
        border: 1px solid rgba(255,255,255,0.05);
        border-radius: 16px;
        margin-bottom: 2.5rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.15);
    }
    .saas-header h1 {
        font-size: 3rem;
        font-weight: 800;
        margin: 0 0 0.5rem 0;
        background: linear-gradient(90deg, #818cf8, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .saas-header p {
        font-size: 1.15rem;
        color: #94a3b8;
        max-width: 600px;
        margin: 0 auto;
        line-height: 1.5;
    }

    /* Streamlit overrides for SaaS containers */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: #1e1e2f;
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    div[data-testid="stVerticalBlockBorderWrapper"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.15);
    }
    
    /* Insight Cards Typography */
    .insight-title {
        font-size: 0.85rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        color: #94a3b8;
        margin-bottom: 0.75rem;
        border-bottom: 1px solid rgba(255,255,255,0.05);
        padding-bottom: 0.5rem;
    }
    
    /* Skill Tags */
    .stag {
        display: inline-block; padding: 0.35rem 0.85rem; margin: 0.2rem;
        border-radius: 8px; font-size: 0.85rem; font-weight: 600;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .stag-green { background: #05966922; color: #10b981; border: 1px solid #10b98144; }
    .stag-red { background: #e11d4822; color: #f43f5e; border: 1px solid #f43f5e44; }

    /* Match Score Text */
    .score-display {
        font-size: 3.5rem;
        font-weight: 800;
        line-height: 1;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ─────────────────────────────────────────────────────────────────────
# Keep the sidebar for thresholds
with st.sidebar:
    st.markdown("## ✨ Vibe Controls")
    threshold = st.slider("Vibe Threshold (%)", 0, 100, 40, 5,
        help="Only candidates scoring at or above this level are considered qualified.")
    st.markdown("---")
    st.markdown("### 🎯 How to Vibe Screen")
    st.markdown("""
1. Drop the Job Description.
2. Formulate Candidate Resumes.
3. Hit **Analyze**.
4. Explore Insight Cards.
    """)
    st.markdown("---")
    st.markdown(
        "<small style='color:#888'>Powered by <code>all-MiniLM-L6-v2</code> vibes<br>"
        "Zero APIs. Zero cost. Pure vibes.</small>",
        unsafe_allow_html=True,
    )

# ── Header ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="saas-header">
    <h1>Vibe Screening AI</h1>
    <p>Seamlessly evaluate candidate resume fit for your job description using advanced semantic matching and skill gap analysis.</p>
</div>
""", unsafe_allow_html=True)

# ── Input Panels ──────────────────────────────────────────────────────────────
col_jd, col_res = st.columns(2, gap="large")

with col_jd:
    with st.container(border=True):
        st.markdown("### 📝 Job Description")
        st.markdown("<div class='insight-title'>Paste Roles & Requirements</div>", unsafe_allow_html=True)
        jd_text = st.text_area("JD", height=280, key="jd_input", label_visibility="collapsed",
            placeholder="e.g. We are looking for a Senior Developer with 5+ years of experience...")

with col_res:
    with st.container(border=True):
        st.markdown("### 📁 Candidate Resumes")
        st.markdown("<div class='insight-title'>Upload Files or Paste Profiles</div>", unsafe_allow_html=True)
        t1, t2 = st.tabs(["Upload Files", "Paste Text"])
        with t1:
            uploaded_files = st.file_uploader("Drop PDF/DOCX (Max 200MB per file)", type=["pdf", "docx"], accept_multiple_files=True, key="file_input", label_visibility="collapsed")
        with t2:
            pasted_resumes_raw = st.text_area("Paste", height=195, key="paste_input", placeholder="Paste resume text. Separate multiples with ---", label_visibility="collapsed")
            parts = [p.strip() for p in pasted_resumes_raw.split("---") if p.strip()] if "paste_input" in st.session_state and st.session_state.paste_input else []

has_input = jd_text and (uploaded_files or parts)

# ── Actions ───────────────────────────────────────────────────────────────────
st.write("") # vertical spacing
btn_col1, btn_col2, btn_col3, btn_col4 = st.columns([1, 2, 2, 1])
with btn_col2:
    analyze_btn = st.button("🚀 Analyze", use_container_width=True, type="primary", disabled=not has_input)
with btn_col3:
    st.button("🔄 Reset", use_container_width=True, on_click=do_reset)
st.write("")
st.markdown("---")

# ── Processing & Results ──────────────────────────────────────────────────────
if analyze_btn and has_input:
    with st.spinner("Analyzing candidate fit..."):
        # Build unified resume list
        resume_items = []
        if uploaded_files:
            for uf in uploaded_files:
                resume_items.append({"type": "file", "name": uf.name, "file": uf})
        for idx, txt in enumerate(parts, 1):
            resume_items.append({"type": "pasted", "name": f"Pasted Resume #{idx}", "text": txt})

        total = len(resume_items)

        # Step 1: Model
        load_model()

        # Step 2: Analyze JD
        jd_analysis = analyze_jd(jd_text)
        jd_embedding = get_embeddings([jd_text])
        jd_skills = jd_analysis["all_skills"]

        # Step 3: Process resumes
        candidates = []
        failed_files = []

        for i, item in enumerate(resume_items):
            fname = item["name"]

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
        candidates.sort(key=lambda c: c["match_score"], reverse=True)
        qualified = [c for c in candidates if c["match_score"] >= threshold]

        # Save session
        session_id = save_session(jd_text, threshold, candidates, failed_files)

    # ══════════════════════════════════════════════════════════════════════════
    # RESULTS (INSIGHT CARDS)
    # ══════════════════════════════════════════════════════════════════════════
    st.markdown("## ✨ Analysis Results")
    
    if candidates:
        for rank, c in enumerate(candidates, 1):
            name = c.get("name") or c.get("source_file", "Unknown")
            score = c["match_score"]
            explanation = c.get("explanation", {})
            matched = c.get("matched_skills", [])
            missing = c.get("missing_skills", [])
            
            with st.container(border=True):
                st.markdown(f"### #{rank} — {name}")
                st.write("") # spacing
                
                # Row 1: Match Score | Candidate Summary
                r1c1, r1c2 = st.columns([1, 2], gap="large")
                with r1c1:
                    with st.container(border=True):
                        st.markdown("<div class='insight-title'>Match Score</div>", unsafe_allow_html=True)
                        color = "#10b981" if score >= 70 else "#f59e0b" if score >= threshold else "#f43f5e"
                        st.markdown(f"""
                        <div class="score-display" style="color: {color};">{score:.1f}%</div>
                        <div style="background: rgba(255,255,255,0.05); border-radius: 99px; height: 10px; width: 100%; margin-top: 15px;">
                            <div style="background: {color}; width: {score}%; height: 100%; border-radius: 99px;"></div>
                        </div>
                        """, unsafe_allow_html=True)
                with r1c2:
                    with st.container(border=True):
                        st.markdown("<div class='insight-title'>Candidate Summary</div>", unsafe_allow_html=True)
                        st.markdown(f"<div style='font-size: 1.1rem; line-height: 1.6; color: #e2e8f0;'>{explanation.get('summary', 'No summary available.')}</div>", unsafe_allow_html=True)
                
                # Row 2: Skills
                r2c1, r2c2 = st.columns(2, gap="large")
                with r2c1:
                    with st.container(border=True):
                        st.markdown("<div class='insight-title'>Matched Skills</div>", unsafe_allow_html=True)
                        if matched:
                            tags = " ".join([f"<span class='stag stag-green'>{s}</span>" for s in matched])
                            st.markdown(tags, unsafe_allow_html=True)
                        else:
                            st.caption("None identified")
                with r2c2:
                    with st.container(border=True):
                        st.markdown("<div class='insight-title'>Missing Skills</div>", unsafe_allow_html=True)
                        if missing:
                            tags = " ".join([f"<span class='stag stag-red'>{s}</span>" for s in missing])
                            st.markdown(tags, unsafe_allow_html=True)
                        else:
                            st.caption("None missing")
                            
                # Row 3: Strengths & Gaps
                r3c1, r3c2 = st.columns(2, gap="large")
                with r3c1:
                    with st.container(border=True):
                        st.markdown("<div class='insight-title'>Strengths</div>", unsafe_allow_html=True)
                        for s in explanation.get('strengths', []):
                            st.markdown(f"✅ {s}")
                with r3c2:
                    with st.container(border=True):
                        st.markdown("<div class='insight-title'>Gaps</div>", unsafe_allow_html=True)
                        gaps = explanation.get('gaps', [])
                        if gaps:
                            for g in gaps:
                                st.markdown(f"⚠️ {g}")
                        else:
                            st.markdown("Minimal gaps detected.")
            
            st.markdown("---")
            
        # Exports
        st.write("")
        dl1, dl2 = st.columns(2)
        excel_bytes = export_to_excel(qualified) if qualified else None
        csv_str = export_to_csv(qualified) if qualified else None
        
        with dl1:
            if excel_bytes:
                st.download_button("📥 Download Excel (Qualified)", data=excel_bytes,
                    file_name="shortlisted_candidates.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True, type="primary")
        with dl2:
            if csv_str:
                st.download_button("📥 Download CSV (Qualified)", data=csv_str,
                    file_name="shortlisted_candidates.csv", mime="text/csv",
                    use_container_width=True)
    else:
        st.warning("No valid resumes were parsed successfully.")

    # Failed files
    if failed_files:
        with st.expander(f"⚠️ {len(failed_files)} file(s) failed parsing"):
            for fn, reason in failed_files:
                st.markdown(f"- **{fn}**: {reason}")

elif not has_input:
    st.info("✨ Drop a JD and upload some resumes to start the vibe check.")
