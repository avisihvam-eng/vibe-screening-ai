"""
Skill Matcher Module
Extracts tech skills from text and computes skill gaps between JD and resume.
Uses keyword matching against a curated skill dictionary.
"""
import re

# ── Skill Dictionary ────────────────────────────────────────────────────────────
# Curated list of ~200 tech skills/tools/frameworks grouped by category.
# Each entry is lowercase for case-insensitive matching.

_SKILLS = {
    # Languages
    "python", "java", "javascript", "typescript", "c++", "c#", "go", "golang",
    "rust", "ruby", "php", "swift", "kotlin", "scala", "r", "sql", "bash",
    "shell", "perl", "matlab", "dart", "lua", "haskell", "elixir",

    # Python Frameworks & Libraries
    "django", "flask", "fastapi", "streamlit", "celery", "sqlalchemy",
    "pydantic", "pytest", "numpy", "pandas", "scipy", "matplotlib",
    "seaborn", "plotly", "beautifulsoup", "scrapy", "asyncio", "uvicorn",

    # ML / AI / Data Science
    "machine learning", "deep learning", "nlp",
    "natural language processing", "computer vision", "reinforcement learning",
    "pytorch", "tensorflow", "keras", "scikit-learn", "sklearn",
    "xgboost", "lightgbm", "catboost", "hugging face", "transformers",
    "spacy", "nltk", "gensim", "opencv", "yolo",
    "langchain", "llamaindex", "llama index", "vector database",
    "rag", "retrieval augmented generation", "fine-tuning", "fine tuning",
    "bert", "gpt", "llm", "large language model",
    "sentence-transformers", "sentence transformers",
    "faiss", "pinecone", "chromadb", "weaviate", "milvus",
    "mlflow", "weights & biases", "wandb", "mlops",
    "feature engineering", "model deployment", "model serving",
    "onnx", "tensorrt", "triton",

    # Data Engineering
    "apache spark", "spark", "pyspark", "hadoop", "hive", "kafka",
    "apache airflow", "airflow", "luigi", "prefect", "dagster",
    "dbt", "etl", "data pipeline", "data warehouse",

    # Databases
    "postgresql", "postgres", "mysql", "sqlite", "oracle",
    "mongodb", "cassandra", "dynamodb", "couchdb",
    "redis", "memcached", "elasticsearch", "neo4j",

    # Cloud & DevOps
    "aws", "amazon web services", "gcp", "google cloud", "azure",
    "docker", "kubernetes", "k8s", "helm", "terraform", "ansible",
    "jenkins", "github actions", "gitlab ci", "circleci", "argocd",
    "ci/cd", "ci cd", "devops",
    "ec2", "s3", "lambda", "ecs", "eks", "fargate", "sagemaker",
    "cloud run", "cloud functions", "bigquery", "gke",

    # Web & APIs
    "rest api", "rest apis", "graphql", "grpc", "websocket",
    "microservices", "api gateway", "oauth", "jwt",

    # Frontend
    "react", "angular", "vue", "vue.js", "next.js", "nextjs",
    "html", "css", "sass", "tailwind", "webpack", "vite",

    # Testing & Quality
    "unit testing", "integration testing", "tdd",
    "selenium", "cypress", "jest", "mocha",

    # Tools & Practices
    "git", "github", "gitlab", "bitbucket",
    "jira", "confluence", "agile", "scrum",
    "linux", "unix", "networking",
    "prometheus", "grafana", "elk", "datadog",
    "rabbitmq", "celery", "sqs", "sns",

    # Data Formats & Misc
    "json", "xml", "yaml", "csv", "parquet", "avro",
    "rest", "soap", "api",
}

# Pre-compile patterns: sort longest first so "machine learning" matches before "machine"
_SKILL_PATTERNS = sorted(_SKILLS, key=len, reverse=True)
_SKILL_RE = re.compile(
    r"\b(" + "|".join(re.escape(s) for s in _SKILL_PATTERNS) + r")\b",
    re.IGNORECASE,
)


def extract_skills(text: str) -> set[str]:
    """Extract all recognized tech skills from text.

    Returns:
        Set of lowercase skill names found in the text.
    """
    matches = _SKILL_RE.findall(text)
    return {m.lower() for m in matches}


def match_skills(
    jd_skills: set[str],
    resume_text: str,
) -> dict[str, list[str]]:
    """Compare JD skills against a resume.

    Args:
        jd_skills: Set of skills extracted from the JD.
        resume_text: Full resume text.

    Returns:
        {"matched": [...], "missing": [...]} — both lists sorted alphabetically.
    """
    resume_skills = extract_skills(resume_text)
    matched = sorted(jd_skills & resume_skills)
    missing = sorted(jd_skills - resume_skills)
    return {"matched": matched, "missing": missing}
