# 📄 AutoResume Filter 40

AI-powered resume screening tool that ranks candidates against a job description using semantic similarity and skill gap analysis.

## Features

- **Semantic Matching** — Uses `all-MiniLM-L6-v2` embeddings to score resumes (not just keyword matching)
- **Skill Gap Analysis** — Shows which JD skills each candidate has vs. is missing
- **Session History** — Every screening session is saved and browsable
- **Dashboard** — Aggregate analytics across all sessions
- **Export** — Download shortlisted candidates as Excel or CSV
- **No API Keys** — Everything runs 100% locally, no paid services

## Quick Start

### 1. Clone & Setup

```bash
git clone https://github.com/YOUR_USERNAME/autoresume-filter-40.git
cd autoresume-filter-40

# Create virtual environment (Python 3.12 or 3.13 recommended)
python -m venv .venv

# Activate it
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run

```bash
streamlit run app.py
```

Open http://localhost:8501 in your browser.

### 3. Use

1. Paste a **Job Description** in the text area
2. Upload **resumes** (PDF and/or DOCX)
3. Click **Process Resumes**
4. View results with match scores and skill gap breakdown
5. Download the shortlist as Excel or CSV

## First Run

The first run downloads the embedding model (~90 MB). After that, it's cached and works **fully offline**.

## Requirements

- Python 3.12 or 3.13 (⚠️ Python 3.14 alpha is NOT supported)
- ~200 MB disk space (for the model)
- Internet connection (first run only)

## Project Structure

```
├── app.py                  # Multi-page app entry point
├── pages/
│   ├── screen.py           # Main screening page
│   ├── history.py          # Session history browser
│   └── dashboard.py        # Analytics dashboard
├── utils/
│   ├── resume_parser.py    # PDF/DOCX text extraction
│   ├── info_extractor.py   # Name/email/phone extraction
│   ├── chunker.py          # Resume text chunking
│   ├── embedder.py         # Embedding model loader
│   ├── scorer.py           # Semantic similarity scoring
│   ├── skill_matcher.py    # Skill gap analysis
│   ├── exporter.py         # Excel/CSV export
│   └── history_store.py    # Session persistence (local JSON)
├── requirements.txt
└── .streamlit/config.toml  # Theme config
```

## License

MIT
