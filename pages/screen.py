"""
Screen Resumes Page
Main screening workflow: upload JD + resumes → process → results with skill gaps.
"""
import streamlit as st
import time

from utils.resume_parser import extract_text
from utils.info_extractor import extract_candidate_info
from utils.chunker import chunk_text
from utils.embedder import get_embeddings, load_model
from utils.scorer import score_candidate, filter_and_rank
from utils.exporter import export_to_excel, export_to_csv
from utils.skill_matcher import extract_skills, match_skills
from utils.history_store import save_session

# ── Custom CSS ──────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main .block-container { padding-top: 1.5rem; }

    .app-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem 2.5rem;
        border-radius: 16px;
        margin-bottom: 1.5rem;
        color: white;
    }
    .app-header h1 { margin: 0; font-size: 2.2rem; font-weight: 700; }
    .app-header p { margin: 0.5rem 0 0 0; opacity: 0.9; font-size: 1.05rem; }

    .metric-row { display: flex; gap: 1rem; margin: 1.5rem 0; }
    .metric-card {
        flex: 1;
        background: linear-gradient(145deg, #1e1e2f, #2a2a40);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 14px;
        padding: 1.4rem 1.6rem;
        text-align: center;
        transition: transform 0.2s;
    }
    .metric-card:hover { transform: translateY(-2px); }
    .metric-card .value {
        font-size: 2.6rem; font-weight: 800;
        background: linear-gradient(90deg, #667eea, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .metric-card .label {
        font-size: 0.85rem; color: #aaa; margin-top: 0.3rem;
        text-transform: uppercase; letter-spacing: 1px;
    }

    .badge-success {
        display: inline-block; padding: 0.25rem 0.75rem;
        background: #22c55e22; color: #22c55e;
        border-radius: 999px; font-size: 0.8rem; font-weight: 600;
    }

    .skill-tag {
        display: inline-block; padding: 0.15rem 0.5rem; margin: 0.1rem;
        border-radius: 6px; font-size: 0.75rem; font-weight: 500;
    }
    .skill-matched {
        background: #22c55e22; color: #22c55e; border: 1px solid #22c55e44;
    }
    .skill-missing {
        background: #ef444422; color: #ef4444; border: 1px solid #ef444444;
    }

    .stDataFrame { border-radius: 12px; overflow: hidden; }
</style>
""", unsafe_allow_html=True)

# ── Header ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="app-header">
    <h1>📄 AutoResume Filter 40</h1>
    <p>Upload a job description + resumes → get a ranked shortlist with skill gap analysis.</p>
</div>
""", unsafe_allow_html=True)

# ── Sidebar ─────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Settings")
    threshold = st.slider(
        "Match Threshold (%)",
        min_value=0,
        max_value=100,
        value=40,
        step=5,
        help="Candidates scoring at or above this threshold will be shortlisted.",
    )
    st.markdown("---")
    st.markdown("### 📋 How It Works")
    st.markdown("""
1. Paste the **Job Description**
2. Upload **resumes** (PDF / DOCX)
3. Click **Process Resumes**
4. View **skill gaps** & download results
    """)
    st.markdown("---")
    st.markdown(
        "<small style='color:#888'>Powered by <code>all-MiniLM-L6-v2</code> embeddings<br>"
        "No paid APIs required</small>",
        unsafe_allow_html=True,
    )

# ── Input Section ───────────────────────────────────────────────────────────────
col_jd, col_resumes = st.columns([1, 1], gap="large")

with col_jd:
    st.markdown("### 📝 Job Description")
    jd_text = st.text_area(
        "Paste the full job description here",
        height=300,
        placeholder="e.g. We are looking for a Senior Python Developer with 5+ years of experience...",
        label_visibility="collapsed",
    )

with col_resumes:
    st.markdown("### 📁 Upload Resumes")
    uploaded_files = st.file_uploader(
        "Upload PDF or DOCX files",
        type=["pdf", "docx"],
        accept_multiple_files=True,
        label_visibility="collapsed",
    )
    if uploaded_files:
        st.markdown(
            f"<span class='badge-success'>✓ {len(uploaded_files)} file(s) selected</span>",
            unsafe_allow_html=True,
        )

# ── Processing ──────────────────────────────────────────────────────────────────
st.markdown("---")

process_btn = st.button(
    "🚀 Process Resumes",
    use_container_width=True,
    type="primary",
    disabled=not (jd_text and uploaded_files),
)

if process_btn and jd_text and uploaded_files:
    total = len(uploaded_files)
    progress = st.progress(0, text="Initializing...")
    status_area = st.empty()

    # Step 1: Load model
    status_area.info("⏳ Loading embedding model (first run downloads ~90 MB)...")
    model = load_model()
    progress.progress(5, text="Model loaded")

    # Step 2: Embed JD + extract skills
    status_area.info("⏳ Embedding job description & extracting skills...")
    jd_embedding = get_embeddings([jd_text])
    jd_skills = extract_skills(jd_text)
    progress.progress(10, text=f"JD embedded — {len(jd_skills)} skills detected")

    # Step 3: Process each resume
    candidates: list[dict] = []
    failed_files: list[tuple[str, str]] = []

    for i, uploaded_file in enumerate(uploaded_files):
        file_name = uploaded_file.name
        pct = 10 + int(75 * (i / total))
        progress.progress(pct, text=f"Processing {file_name} ({i+1}/{total})")
        status_area.info(f"⏳ Processing **{file_name}**...")

        # Parse
        file_bytes = uploaded_file.read()
        text, err = extract_text(file_name, file_bytes)
        if err:
            failed_files.append((file_name, err))
            continue

        # Extract info
        info = extract_candidate_info(text)

        # Chunk & Score
        chunks = chunk_text(text)
        if not chunks:
            failed_files.append((file_name, "Resume too short to process"))
            continue

        score = score_candidate(jd_embedding, chunks)

        # Skill gap
        skill_result = match_skills(jd_skills, text)

        candidate = {
            "name": info["name"],
            "email": info["email"],
            "phone": info["phone"],
            "location": info["location"],
            "linkedin": info["linkedin"],
            "match_score": score,
            "matched_skills": skill_result["matched"],
            "missing_skills": skill_result["missing"],
            "notes": "",
            "source_file": file_name,
        }
        candidates.append(candidate)

    progress.progress(88, text="Filtering & ranking...")

    # Step 4: Filter & rank
    qualified = filter_and_rank(candidates, threshold=threshold)

    # Step 5: Save session
    progress.progress(92, text="Saving session...")
    session_id = save_session(jd_text, threshold, candidates, failed_files)

    # Step 6: Export
    progress.progress(96, text="Generating exports...")
    excel_bytes = export_to_excel(qualified) if qualified else None
    csv_str = export_to_csv(qualified) if qualified else None

    progress.progress(100, text="✅ Done!")
    status_area.empty()
    time.sleep(0.3)
    progress.empty()

    # ── Results ─────────────────────────────────────────────────────────────
    st.markdown("## 📊 Results")
    st.caption(f"Session: `{session_id}` — saved to history")

    # Metric cards
    st.markdown(f"""
    <div class="metric-row">
        <div class="metric-card">
            <div class="value">{total}</div>
            <div class="label">Total Resumes</div>
        </div>
        <div class="metric-card">
            <div class="value">{len(candidates)}</div>
            <div class="label">Parsed OK</div>
        </div>
        <div class="metric-card">
            <div class="value">{len(qualified)}</div>
            <div class="label">Qualified (≥ {threshold}%)</div>
        </div>
        <div class="metric-card">
            <div class="value">{len(failed_files)}</div>
            <div class="label">Failed / Skipped</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Skills detected in JD
    if jd_skills:
        with st.expander(f"🎯 {len(jd_skills)} skills detected in JD", expanded=False):
            skills_html = " ".join(
                f"<span class='skill-tag skill-matched'>{s}</span>" for s in sorted(jd_skills)
            )
            st.markdown(skills_html, unsafe_allow_html=True)

    # Qualified candidates table
    if qualified:
        import pandas as pd
        df = pd.DataFrame([{
            "Name": c.get("name") or "N/A",
            "Email": c.get("email") or "N/A",
            "Phone": c.get("phone") or "N/A",
            "Match Score (%)": c.get("match_score", 0),
            "Matched Skills": len(c.get("matched_skills", [])),
            "Missing Skills": len(c.get("missing_skills", [])),
        } for c in qualified])

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Match Score (%)": st.column_config.ProgressColumn(
                    "Match Score (%)",
                    min_value=0,
                    max_value=100,
                    format="%.1f%%",
                ),
            },
        )

        # Skill gap details per candidate
        for c in qualified:
            name = c.get("name") or c.get("source_file", "Unknown")
            matched = c.get("matched_skills", [])
            missing = c.get("missing_skills", [])
            with st.expander(f"🔬 {name} — {len(matched)} matched, {len(missing)} missing"):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**✅ Matched Skills**")
                    if matched:
                        html = " ".join(f"<span class='skill-tag skill-matched'>{s}</span>" for s in matched)
                        st.markdown(html, unsafe_allow_html=True)
                    else:
                        st.caption("None detected")
                with col2:
                    st.markdown("**❌ Missing Skills**")
                    if missing:
                        html = " ".join(f"<span class='skill-tag skill-missing'>{s}</span>" for s in missing)
                        st.markdown(html, unsafe_allow_html=True)
                    else:
                        st.caption("All skills matched!")

        # Download buttons
        dl_col1, dl_col2 = st.columns(2)
        with dl_col1:
            st.download_button(
                label="📥 Download Excel",
                data=excel_bytes,
                file_name="shortlisted_candidates.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                type="primary",
            )
        with dl_col2:
            st.download_button(
                label="📥 Download CSV",
                data=csv_str,
                file_name="shortlisted_candidates.csv",
                mime="text/csv",
                use_container_width=True,
            )
    else:
        st.warning(
            f"No candidates matched at ≥ {threshold}% threshold. "
            "Try lowering the threshold in the sidebar."
        )

    # Failed files
    if failed_files:
        with st.expander(f"⚠️ {len(failed_files)} file(s) failed to parse", expanded=False):
            for fname, reason in failed_files:
                st.markdown(f"- **{fname}**: {reason}")

    # Below threshold
    below = [c for c in candidates if c["match_score"] < threshold]
    if below:
        with st.expander(f"📉 {len(below)} candidate(s) below threshold", expanded=False):
            import pandas as pd
            df_below = pd.DataFrame([{
                "Name": c.get("name") or "N/A",
                "Source File": c.get("source_file", ""),
                "Match Score (%)": c.get("match_score", 0),
                "Missing Skills": len(c.get("missing_skills", [])),
            } for c in sorted(below, key=lambda x: x["match_score"], reverse=True)])
            st.dataframe(df_below, use_container_width=True, hide_index=True)

elif not jd_text and not uploaded_files:
    st.info("👆 Paste a job description and upload resumes to get started.")
elif not jd_text:
    st.warning("⚠️ Please paste a job description.")
elif not uploaded_files:
    st.warning("⚠️ Please upload at least one resume (PDF or DOCX).")
