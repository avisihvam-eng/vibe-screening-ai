"""
Resume Analyzer Module
Extracts structured candidate profile from resume text using regex + heuristics.
No LLM needed.
"""
import re
from datetime import datetime
from utils.skill_matcher import extract_skills

# ── Date Patterns ───────────────────────────────────────────────────────────────
_MONTH_NAMES = (
    r"(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|"
    r"jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)"
)

_DATE_RANGE_RE = re.compile(
    rf"({_MONTH_NAMES}[\s,]*\d{{4}}|(?:\d{{1,2}}[/\-])?(?:\d{{4}}))"
    r"\s*[\-–—to]+\s*"
    rf"({_MONTH_NAMES}[\s,]*\d{{4}}|(?:\d{{1,2}}[/\-])?(?:\d{{4}})|present|current|now|ongoing)",
    re.IGNORECASE,
)

_YEAR_RE = re.compile(r"\b(20\d{2}|19\d{2})\b")

_EXPERIENCE_YEARS_RE = re.compile(
    r"(\d+)\+?\s*(?:years?|yrs?)\s*(?:of\s+)?(?:experience|exp|professional)?",
    re.IGNORECASE,
)

# ── Education Patterns ──────────────────────────────────────────────────────────
_DEGREE_RE = re.compile(
    r"(?:B\.?(?:Tech|Eng|Sc|A|Com|S)|M\.?(?:Tech|Eng|Sc|S|A|Com|BA)|"
    r"Ph\.?D|MBA|BCA|MCA|BE|ME|BS|MS|"
    r"Bachelor(?:'s)?|Master(?:'s)?|Doctorate|Diploma)",
    re.IGNORECASE,
)

_EDUCATION_SECTION_RE = re.compile(
    r"(?:^|\n)\s*(?:education|academic|qualification|degree)s?\s*[:\-]?\s*\n",
    re.IGNORECASE,
)

# ── Company Patterns ────────────────────────────────────────────────────────────
_EXPERIENCE_SECTION_RE = re.compile(
    r"(?:^|\n)\s*(?:experience|employment|work\s*history|career|professional\s*experience)"
    r"\s*[:\-]?\s*\n",
    re.IGNORECASE,
)

_COMPANY_TITLE_RE = re.compile(
    r"(?:^|\n)\s*(?:at|@)?\s*([A-Z][A-Za-z\s&\.\,]+(?:Inc|Corp|Ltd|LLC|Technologies|Tech|"
    r"Solutions|Systems|Software|Labs|Studio|Digital|Analytics|Consulting|"
    r"Services|Group|Networks|Platform|AI|Pvt)\.?)\s*(?:[\-–—|,]|$)",
    re.MULTILINE,
)

# ── Project Patterns ────────────────────────────────────────────────────────────
_PROJECTS_SECTION_RE = re.compile(
    r"(?:^|\n)\s*(?:projects?|key\s*projects?|notable\s*projects?|personal\s*projects?)"
    r"\s*[:\-]?\s*\n",
    re.IGNORECASE,
)


def _parse_year(date_str: str) -> int | None:
    """Extract year from a date string."""
    m = _YEAR_RE.search(date_str)
    return int(m.group(1)) if m else None


def _extract_date_ranges(text: str) -> list[tuple[int | None, int | None]]:
    """Extract (start_year, end_year) pairs from date ranges in text."""
    ranges = []
    for m in _DATE_RANGE_RE.finditer(text):
        start = _parse_year(m.group(1))
        end_str = m.group(2).strip().lower()
        if end_str in ("present", "current", "now", "ongoing"):
            end = datetime.now().year
        else:
            end = _parse_year(m.group(2))
        ranges.append((start, end))
    return ranges


def _estimate_years_of_experience(text: str) -> float | None:
    """Estimate total years of experience."""
    # Method 1: Explicit mention ("5+ years of experience")
    explicit = _EXPERIENCE_YEARS_RE.findall(text)
    if explicit:
        return max(int(y) for y in explicit)

    # Method 2: Sum up date ranges
    ranges = _extract_date_ranges(text)
    if ranges:
        total_years = 0
        for start, end in ranges:
            if start and end:
                total_years += max(0, end - start)
        if total_years > 0:
            return total_years

    return None


def _extract_section(text: str, header_re: re.Pattern, max_chars: int = 1500) -> str:
    """Extract text under a section header."""
    m = header_re.search(text)
    if not m:
        return ""
    start = m.end()
    # End at next section-like header or max_chars
    next_header = re.search(
        r"\n\s*(?:[A-Z][A-Z\s]{3,}|#{1,3}\s)\s*[:\-]?\s*\n",
        text[start : start + max_chars],
    )
    end = start + (next_header.start() if next_header else max_chars)
    return text[start:end].strip()


def _extract_companies(text: str) -> list[str]:
    """Extract company names from experience section."""
    exp_text = _extract_section(text, _EXPERIENCE_SECTION_RE)
    if not exp_text:
        exp_text = text  # fallback to full text

    companies = []
    for m in _COMPANY_TITLE_RE.finditer(exp_text):
        name = m.group(1).strip().rstrip(",. ")
        if len(name) > 2 and name not in companies:
            companies.append(name)

    # Fallback: look for "at CompanyName" patterns
    if not companies:
        at_pattern = re.findall(
            r"(?:at|@)\s+([A-Z][A-Za-z\s&]+?)(?:\s*[\-–—,|]|\s*\n)",
            text[:3000],
        )
        companies = list(dict.fromkeys(c.strip() for c in at_pattern if len(c.strip()) > 2))

    return companies[:8]


def _extract_education(text: str) -> list[str]:
    """Extract education entries."""
    edu_text = _extract_section(text, _EDUCATION_SECTION_RE)
    if not edu_text:
        edu_text = text[:3000]

    entries = []
    for line in edu_text.split("\n"):
        line = line.strip()
        if _DEGREE_RE.search(line) and len(line) > 5:
            cleaned = re.sub(r"^[\-\*\•\d+[\.\)]\s*", "", line).strip()
            if cleaned and cleaned not in entries:
                entries.append(cleaned[:120])

    return entries[:5]


def _extract_projects(text: str) -> list[str]:
    """Extract project names/descriptions."""
    proj_text = _extract_section(text, _PROJECTS_SECTION_RE)
    if not proj_text:
        return []

    projects = []
    for line in proj_text.split("\n"):
        line = line.strip()
        cleaned = re.sub(r"^[\-\*\•\d+[\.\)]\s*", "", line).strip()
        if cleaned and len(cleaned) > 5:
            projects.append(cleaned[:150])

    return projects[:8]


def analyze_resume(text: str) -> dict:
    """Extract structured profile from resume text.

    Returns:
        {
            "experience_years": float or None,
            "companies": [...],
            "education": [...],
            "skills": [...],
            "projects": [...],
            "date_ranges": [...],
            "has_linkedin": bool,
        }
    """
    skills = extract_skills(text)
    experience_years = _estimate_years_of_experience(text)
    companies = _extract_companies(text)
    education = _extract_education(text)
    projects = _extract_projects(text)
    date_ranges = _extract_date_ranges(text)
    has_linkedin = bool(re.search(r"linkedin\.com/in/", text, re.IGNORECASE))

    return {
        "experience_years": experience_years,
        "companies": companies,
        "education": education,
        "skills": sorted(skills),
        "projects": projects,
        "date_ranges": date_ranges,
        "has_linkedin": has_linkedin,
    }
