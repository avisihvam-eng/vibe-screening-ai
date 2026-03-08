# ✨ Vibe Screening AI

> *"Traditional screening: Read 500 resumes, cry, hire someone random.*
> *Vibe screening: Let AI read 500 resumes, sip chai, hire someone good."*

AI-powered resume screening that actually understands what candidates are about — not just keyword bingo.

## What it Does

Drop a **job description**, throw in a pile of **resumes** (PDF or DOCX), and let the AI figure out who's got the right vibes. You'll get:

- **Semantic matching** — understands meaning, not just keywords. "ML Engineer" and "Machine Learning Developer" = same vibe ✨
- **Skill gap analysis** — shows exactly which skills each candidate has vs. what they're missing
- **Ranked shortlist** — top candidates float up, irrelevant profiles sink down
- **Session history** — every vibe check is saved so you can revisit past screenings
- **Dashboard** — aggregate stats across all your screenings
- **Excel + CSV export** — download the shortlist for your ATS, your boss, or your WhatsApp group

## What it Does NOT Do

- ❌ **Replace your judgment** — it ranks, you decide
- ❌ **Cost money** — no API keys, no subscriptions, no "upgrade to Pro" bs
- ❌ **Send your data anywhere** — everything runs 100% locally on your machine
- ❌ **Care about fancy resume fonts** — it reads content, not design
- ❌ **Work miracles on potato-quality PDFs** — garbage in, garbage out

## Quick Start

```bash
# Clone
git clone https://github.com/avisihvam-eng/autoresume-filter-40.git
cd autoresume-filter-40

# Setup (Python 3.12 or 3.13 — NOT 3.14 alpha)
python -m venv .venv
.venv\Scripts\activate       # Windows
# source .venv/bin/activate  # macOS/Linux

# Install
pip install -r requirements.txt

# Run
streamlit run app.py
```

Open http://localhost:8501 and start vibe checking.

> **First run** downloads the AI model (~90 MB). After that, it works fully offline.

## Project Structure

```
├── app.py                  # Multi-page entry point
├── pages/
│   ├── screen.py           # ✨ Vibe Check — main screening
│   ├── history.py          # 📜 Past Vibes — session browser
│   └── dashboard.py        # 📊 Vibe Dashboard — analytics
├── utils/
│   ├── resume_parser.py    # PDF/DOCX text extraction
│   ├── info_extractor.py   # Name/email/phone extraction
│   ├── chunker.py          # Resume text chunking
│   ├── embedder.py         # Embedding model (all-MiniLM-L6-v2)
│   ├── scorer.py           # Semantic similarity scoring
│   ├── skill_matcher.py    # Skill gap analysis (~200 tech skills)
│   ├── exporter.py         # Excel/CSV export
│   └── history_store.py    # Session persistence (local JSON)
├── requirements.txt
└── .streamlit/config.toml
```

## Built With

- [Streamlit](https://streamlit.io) — UI framework
- [sentence-transformers](https://www.sbert.net) — semantic embeddings
- [PyPDF2](https://pypdf2.readthedocs.io) — PDF parsing
- Pure vibes ✨

## License

MIT — do whatever you want with it. Just don't blame us if you hire someone who lists "vibes" as a skill.
