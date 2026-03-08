"""
Generate test data for AutoResume Filter 40.
Creates a sample job description (JD.txt) and 10 dummy resumes
(mix of PDF and DOCX) in a `test_data/` folder.

Resumes are designed with different match levels:
  - 3 strong matches  (should pass 40% threshold)
  - 3 moderate matches (borderline)
  - 4 weak/no matches  (should fail)
"""
import os
import io
import zipfile
import xml.etree.ElementTree as ET
from fpdf import FPDF

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "test_data")

# ── Job Description ─────────────────────────────────────────────────────────────

JD_TEXT = """Senior Python Developer – AI/ML Platform

Location: Bangalore, India (Hybrid)
Experience: 5+ years

About the Role:
We are looking for a Senior Python Developer to build and scale our AI/ML platform.
You will work on NLP pipelines, model training infrastructure, and REST APIs that
serve machine learning predictions at scale.

Key Responsibilities:
- Design and develop production-grade Python applications and REST APIs
- Build and optimize NLP/ML pipelines using transformers, spaCy, and scikit-learn
- Deploy models using Docker, Kubernetes, and cloud platforms (AWS/GCP)
- Implement data pipelines with Apache Airflow and Spark
- Write clean, testable code with pytest and CI/CD integration
- Collaborate with data scientists to productionize research prototypes

Requirements:
- 5+ years of professional Python development experience
- Strong experience with FastAPI or Flask for building REST APIs
- Hands-on with NLP libraries (Hugging Face Transformers, spaCy, NLTK)
- Experience with ML frameworks (PyTorch, TensorFlow, scikit-learn)
- Proficiency in SQL and NoSQL databases (PostgreSQL, MongoDB, Redis)
- Experience with Docker, Kubernetes, and CI/CD pipelines
- Strong understanding of software engineering best practices
- Experience with cloud platforms (AWS or GCP)

Nice to Have:
- Experience with LangChain, LlamaIndex, or vector databases
- Knowledge of MLOps tools (MLflow, Weights & Biases)
- Contributions to open-source projects
- Published research or blog posts on AI/ML topics

Compensation: ₹25–40 LPA based on experience
"""

# ── Resume Templates ────────────────────────────────────────────────────────────

RESUMES = [
    # ── STRONG MATCHES ──────────────────────────────────────────────────────────
    {
        "filename": "Arjun_Mehta_Resume.pdf",
        "content": """Arjun Mehta
arjun.mehta@gmail.com | +91 98765 43210
Bangalore, India
linkedin.com/in/arjunmehta

SUMMARY
Senior Python Developer with 7 years of experience building AI/ML platforms,
NLP pipelines, and scalable REST APIs. Expert in transformers, FastAPI, and
cloud-native deployments on AWS.

EXPERIENCE

Lead ML Engineer — DataMind AI, Bangalore (2021–Present)
- Built an end-to-end NLP pipeline using Hugging Face Transformers and spaCy
  for document classification, achieving 94% accuracy
- Designed and deployed REST APIs with FastAPI serving 50K+ predictions/day
- Orchestrated ML workflows using Apache Airflow and Kubernetes on AWS EKS
- Implemented vector search with Pinecone for semantic retrieval (RAG pipeline)
- Led a team of 4 engineers; established CI/CD with GitHub Actions and pytest

Senior Python Developer — TechStack Solutions, Pune (2018–2021)
- Developed microservices in Python/Flask handling 10M+ API calls/month
- Built data pipelines with Apache Spark and PostgreSQL
- Integrated scikit-learn models into production with Docker containers
- Mentored 3 junior developers on clean code practices

Python Developer — CodeCraft Labs, Hyderabad (2017–2018)
- Built web scraping and data processing tools in Python
- Developed REST APIs with Django REST Framework
- Wrote unit tests with pytest achieving 90%+ coverage

SKILLS
Python, FastAPI, Flask, PyTorch, Transformers, spaCy, scikit-learn, Docker,
Kubernetes, AWS (ECS, Lambda, S3), PostgreSQL, MongoDB, Redis, Airflow,
Git, pytest, LangChain, MLflow

EDUCATION
B.Tech Computer Science — IIT Bombay (2017)
""",
    },
    {
        "filename": "Priya_Sharma_Resume.docx",
        "content": """Priya Sharma
priya.sharma@outlook.com | +91 87654 32109
Hyderabad, India
linkedin.com/in/priyasharma-ml

SUMMARY
AI/ML Engineer with 6 years of experience specializing in NLP, deep learning,
and production ML systems. Passionate about building intelligent applications
that solve real-world problems.

EXPERIENCE

Senior ML Engineer — NeuralWorks AI, Hyderabad (2020–Present)
- Developed named entity recognition (NER) and text classification systems
  using Hugging Face Transformers and fine-tuned BERT models
- Built inference APIs with FastAPI, deployed on GCP Cloud Run
- Implemented MLOps pipelines using MLflow and Weights & Biases
- Created semantic search engine using FAISS and sentence-transformers
- Reduced model inference latency by 40% through ONNX optimization

ML Engineer — DataPulse Analytics, Bangalore (2018–2020)
- Built recommendation engine using collaborative filtering and deep learning
- Developed data preprocessing pipelines with pandas and Apache Spark
- Deployed models with Docker and Kubernetes on AWS
- Wrote comprehensive tests with pytest; maintained 85%+ code coverage

Software Developer — InfoSys, Mysore (2017–2018)
- Full-stack Python development with Django and React
- Database design and optimization with PostgreSQL
- REST API development and integration testing

SKILLS
Python, PyTorch, TensorFlow, Transformers, spaCy, NLTK, FastAPI, Flask,
Docker, Kubernetes, GCP, AWS, PostgreSQL, MongoDB, Redis, MLflow, W&B,
Airflow, LangChain, FAISS, Git, pytest

EDUCATION
M.Tech AI & ML — IIIT Hyderabad (2017)
B.Tech CS — NIT Warangal (2015)

PUBLICATIONS
- "Efficient NER for Indian Languages" — EMNLP Workshop 2022
""",
    },
    {
        "filename": "Rahul_Verma_Resume.pdf",
        "content": """Rahul Verma
rahul.verma@protonmail.com | +91 76543 21098
Bangalore, India
linkedin.com/in/rahulverma-dev

PROFESSIONAL SUMMARY
Full-stack Python developer with 5 years of experience, transitioning into AI/ML.
Strong background in building scalable APIs, data pipelines, and deploying
machine learning models in production environments.

WORK EXPERIENCE

Python Developer / ML Engineer — QuantumLeap Tech, Bangalore (2021–Present)
- Building NLP-powered chatbot using LangChain, GPT-4, and vector databases
- Developed REST APIs with FastAPI for ML model serving
- Implemented data ingestion pipelines using Airflow and Spark
- Deployed applications with Docker and Kubernetes on AWS EKS
- Set up monitoring and alerting with Prometheus and Grafana

Backend Developer — CloudNine Software, Chennai (2019–2021)
- Built high-performance REST APIs with Flask and SQLAlchemy
- Designed PostgreSQL schemas and optimized complex queries
- Implemented message queues with RabbitMQ and Celery
- CI/CD pipelines with Jenkins and Docker

Junior Developer — WebWorks Studio, Bangalore (2018–2019)
- Python scripting and automation
- Django web application development
- Unit testing with pytest

TECHNICAL SKILLS
Languages: Python, JavaScript, SQL
ML/AI: scikit-learn, PyTorch, Transformers, LangChain, spaCy
Backend: FastAPI, Flask, Django, Celery
Databases: PostgreSQL, MongoDB, Redis, Elasticsearch
DevOps: Docker, Kubernetes, AWS, Terraform, GitHub Actions
Tools: Git, pytest, Airflow, Spark

EDUCATION
B.E. Computer Science — BMS College of Engineering, Bangalore (2018)
""",
    },

    # ── MODERATE MATCHES ────────────────────────────────────────────────────────
    {
        "filename": "Sneha_Patel_Resume.docx",
        "content": """Sneha Patel
sneha.patel@yahoo.com | +91 65432 10987
Mumbai, India

SUMMARY
Backend developer with 4 years of Python experience. Familiar with basic ML
concepts and eager to grow in the AI/ML space.

EXPERIENCE

Backend Developer — FinTech Innovations, Mumbai (2021–Present)
- Developed REST APIs using Flask and SQLAlchemy
- Built background task processing with Celery and Redis
- Database management with PostgreSQL and MongoDB
- Containerized applications with Docker

Junior Developer — WebSoft Solutions, Pune (2020–2021)
- Python script development and automation
- Basic data analysis with pandas and NumPy
- Django web application maintenance

SKILLS
Python, Flask, Django, PostgreSQL, MongoDB, Redis, Docker, Git,
pandas, NumPy, basic scikit-learn, HTML, CSS, JavaScript

EDUCATION
B.Tech IT — Mumbai University (2020)
""",
    },
    {
        "filename": "Vikram_Singh_Resume.pdf",
        "content": """Vikram Singh
vikram.singh@gmail.com | +91 54321 09876
Delhi, India
linkedin.com/in/vikramsingh

SUMMARY
Data Scientist with 3 years of experience in statistical modeling and machine learning.
Looking to transition into ML engineering roles.

EXPERIENCE

Data Scientist — Analytix Corp, Delhi (2022–Present)
- Built classification and regression models using scikit-learn and XGBoost
- Text analysis using NLTK and basic transformer models
- Data visualization with matplotlib and Plotly
- Jupyter notebook-based analysis and reporting

Associate Data Analyst — DataDriven Inc, Gurgaon (2021–2022)
- SQL queries and data extraction from large databases
- Python scripting for data cleaning and transformation
- Dashboard creation with Tableau

SKILLS
Python, scikit-learn, XGBoost, NLTK, pandas, NumPy, SQL, Tableau,
matplotlib, Jupyter, basic PyTorch, Git

EDUCATION
M.Sc Statistics — Delhi University (2021)
B.Sc Mathematics — Delhi University (2019)
""",
    },
    {
        "filename": "Ananya_Krishnan_Resume.docx",
        "content": """Ananya Krishnan
ananya.k@gmail.com | +91 43210 98765
Chennai, India

PROFESSIONAL SUMMARY
Software engineer with 4 years of Python and Java experience. Some exposure
to ML through personal projects and online courses.

EXPERIENCE

Software Engineer — TCS Digital, Chennai (2021–Present)
- Full-stack development with Python/Django and React
- REST API development and microservices architecture
- Database optimization with Oracle and PostgreSQL
- Agile development methodology

Associate Engineer — Wipro, Bangalore (2020–2021)
- Java and Python application development
- Unit testing and code reviews
- Bug fixing and maintenance

PERSONAL PROJECTS
- Sentiment analysis tool using Python and TextBlob
- Movie recommendation system with collaborative filtering

SKILLS
Python, Java, Django, React, PostgreSQL, Oracle, Docker, Git,
basic ML (scikit-learn, TextBlob), HTML, CSS

EDUCATION
B.Tech CSE — Anna University, Chennai (2020)
""",
    },

    # ── WEAK / NO MATCHES ───────────────────────────────────────────────────────
    {
        "filename": "Deepak_Gupta_Resume.pdf",
        "content": """Deepak Gupta
deepak.gupta@email.com | +91 32109 87654
Noida, India

SUMMARY
Frontend developer specializing in React and Angular with 5 years of experience.
Passionate about creating beautiful and responsive user interfaces.

EXPERIENCE

Senior Frontend Developer — UILabs, Noida (2021–Present)
- Built complex SPAs with React, Redux, and TypeScript
- Implemented responsive designs with CSS Grid and Flexbox
- Performance optimization and lazy loading strategies
- A/B testing and user analytics integration

Frontend Developer — PixelPerfect, Gurgaon (2019–2021)
- Angular application development
- Cross-browser compatibility testing
- Sass/SCSS styling and animation

Junior Developer — WebStudio, Delhi (2018–2019)
- HTML, CSS, JavaScript development
- jQuery plugin integration
- WordPress theme customization

SKILLS
React, Angular, TypeScript, JavaScript, HTML5, CSS3, Sass,
Redux, Next.js, Webpack, Figma, Jest, Cypress

EDUCATION
BCA — Amity University (2018)
""",
    },
    {
        "filename": "Meera_Nair_Resume.docx",
        "content": """Meera Nair
meera.nair@outlook.com | +91 21098 76543
Kochi, India

SUMMARY
HR professional with 6 years of experience in talent acquisition,
employee engagement, and organizational development.

EXPERIENCE

Senior HR Business Partner — GlobalTech, Kochi (2021–Present)
- Managing end-to-end recruitment for technology teams
- Employee engagement initiatives and retention strategies
- Performance management and career development programs
- HR analytics and reporting using Excel and Power BI

HR Executive — PeoplePlus, Bangalore (2019–2021)
- Campus recruitment and lateral hiring
- Onboarding and induction programs
- Compensation benchmarking and benefits administration

HR Coordinator — StartupHub, Trivandrum (2018–2019)
- Administrative HR tasks
- Payroll coordination
- Employee records management

SKILLS
Talent Acquisition, Employee Engagement, HRIS, SAP SuccessFactors,
Microsoft Office, Power BI, Interview Assessment, Team Building

EDUCATION
MBA HR — XLRI Jamshedpur (2018)
BBA — Christ University, Bangalore (2016)
""",
    },
    {
        "filename": "Karthik_Reddy_Resume.pdf",
        "content": """Karthik Reddy
karthik.r@gmail.com | +91 10987 65432
Pune, India

SUMMARY
DevOps engineer with 4 years of experience in CI/CD, cloud infrastructure,
and container orchestration. No software development experience.

EXPERIENCE

DevOps Engineer — CloudOps Solutions, Pune (2021–Present)
- Managing AWS infrastructure with Terraform and CloudFormation
- Kubernetes cluster management and Helm chart development
- CI/CD pipeline setup with Jenkins, GitLab CI, and ArgoCD
- Monitoring with Prometheus, Grafana, and ELK stack
- Incident management and on-call rotations

Junior DevOps — InfraCore, Hyderabad (2020–2021)
- Linux server administration
- Bash scripting and automation
- Docker containerization
- Basic networking and firewall configuration

SKILLS
AWS, Kubernetes, Docker, Terraform, Ansible, Jenkins, GitLab CI,
Prometheus, Grafana, Linux, Bash, Networking, Helm

EDUCATION
B.Tech ECE — JNTU Hyderabad (2020)
""",
    },
    {
        "filename": "Lakshmi_Iyer_Resume.pdf",
        "content": """Lakshmi Iyer
lakshmi.iyer@gmail.com | +91 09876 54321
Coimbatore, India

SUMMARY
Mechanical engineer with 3 years of experience in manufacturing and CAD design.
Looking to transition into technology.

EXPERIENCE

Design Engineer — AutoTech Manufacturing, Coimbatore (2022–Present)
- 3D modeling and simulation using SolidWorks and ANSYS
- Manufacturing process optimization
- Quality control and six sigma methodologies
- Vendor management and procurement

Junior Engineer — MetalWorks India, Chennai (2021–2022)
- Production planning and scheduling
- CNC machine operation and maintenance
- Technical drawing and blueprint reading

SKILLS
SolidWorks, AutoCAD, ANSYS, CATIA, MS Office, Six Sigma Green Belt,
Manufacturing Process, Quality Control, Project Management

EDUCATION
B.E. Mechanical Engineering — PSG Tech, Coimbatore (2021)

CERTIFICATIONS
- Six Sigma Green Belt (ASQ)
- SolidWorks Professional Certification
""",
    },
]


# ── File Generators ─────────────────────────────────────────────────────────────

def create_pdf(filepath: str, text: str):
    """Create a simple PDF with the given text content."""
    # Sanitize Unicode chars that Helvetica (latin-1) can't render
    text = (text
            .replace("\u2014", "-")   # em-dash
            .replace("\u2013", "-")   # en-dash
            .replace("\u2018", "'")   # left single quote
            .replace("\u2019", "'")   # right single quote
            .replace("\u201c", '"')   # left double quote
            .replace("\u201d", '"')   # right double quote
            .replace("\u20b9", "INR") # rupee sign
            .replace("\u2026", "...") # ellipsis
            )
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Helvetica", size=10)
    for line in text.strip().split("\n"):
        if line.strip().isupper() and len(line.strip()) > 2:
            pdf.set_font("Helvetica", "B", 11)
            pdf.cell(0, 6, line.strip(), new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Helvetica", size=10)
        elif line.strip() == "":
            pdf.ln(3)
        else:
            pdf.cell(0, 5, line.rstrip(), new_x="LMARGIN", new_y="NEXT")
    pdf.output(filepath)


def create_docx(filepath: str, text: str):
    """Create a minimal DOCX using stdlib zip + XML (no lxml needed)."""
    WORD_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
    REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
    CT_NS = "http://schemas.openxmlformats.org/package/2006/content-types"
    DOC_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument"

    # Build document.xml
    body_xml = f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    body_xml += f'<w:document xmlns:w="{WORD_NS}"><w:body>'
    for line in text.strip().split("\n"):
        safe = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        body_xml += f'<w:p><w:r><w:t xml:space="preserve">{safe}</w:t></w:r></w:p>'
    body_xml += "</w:body></w:document>"

    # Build supporting XML files
    content_types = f'<?xml version="1.0" encoding="UTF-8"?>'
    content_types += f'<Types xmlns="{CT_NS}">'
    content_types += '<Default Extension="xml" ContentType="application/xml"/>'
    content_types += '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
    content_types += '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
    content_types += "</Types>"

    rels = f'<?xml version="1.0" encoding="UTF-8"?>'
    rels += f'<Relationships xmlns="{REL_NS}">'
    rels += f'<Relationship Id="rId1" Type="{DOC_REL}" Target="word/document.xml"/>'
    rels += "</Relationships>"

    with zipfile.ZipFile(filepath, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", content_types)
        zf.writestr("_rels/.rels", rels)
        zf.writestr("word/document.xml", body_xml)


# ── Main ────────────────────────────────────────────────────────────────────────

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Save JD
    jd_path = os.path.join(OUTPUT_DIR, "JD.txt")
    with open(jd_path, "w", encoding="utf-8") as f:
        f.write(JD_TEXT.strip())
    print(f"  [OK] {jd_path}")

    # Generate resumes
    for resume in RESUMES:
        fpath = os.path.join(OUTPUT_DIR, resume["filename"])
        if fpath.endswith(".pdf"):
            create_pdf(fpath, resume["content"])
        elif fpath.endswith(".docx"):
            create_docx(fpath, resume["content"])
        print(f"  [OK] {resume['filename']}")

    print(f"\n  Done! {len(RESUMES)} resumes + 1 JD saved to: {OUTPUT_DIR}")
    print(f"\n  Expected results at 40% threshold:")
    print(f"    PASS:  Arjun Mehta, Priya Sharma, Rahul Verma (strong match)")
    print(f"    MAYBE: Sneha Patel, Vikram Singh, Ananya Krishnan (borderline)")
    print(f"    FAIL:  Deepak Gupta, Meera Nair, Karthik Reddy, Lakshmi Iyer")


if __name__ == "__main__":
    main()
