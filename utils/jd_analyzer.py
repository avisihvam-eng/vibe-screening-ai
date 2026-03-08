"""
JD Analyzer Module
Extracts structured intelligence from job descriptions using regex + keyword patterns.
No LLM needed — uses section-header detection and proximity matching.
"""
import re
from utils.skill_matcher import extract_skills

# ── Section Header Patterns ─────────────────────────────────────────────────────
_SECTION_RE = re.compile(
    r"(?:^|\n)\s*(?:#{1,3}\s*)?(?:\d+[\.\)]\s*)?"
    r"(required|must have|mandatory|minimum|essential|"
    r"preferred|nice to have|bonus|desired|good to have|"
    r"responsibilities|duties|what you.?ll do|role|"
    r"qualifications|requirements|skills|technologies|tech stack|"
    r"experience|about the role|overview|who you are)"
    r"[:\s\-]*\n?",
    re.IGNORECASE | re.MULTILINE,
)

_EXPERIENCE_RE = re.compile(
    r"(\d+)\s*[\+\-–—to\s]*\s*(\d+)?\s*(?:years?|yrs?)\s*(?:of\s+)?(?:experience|exp)?",
    re.IGNORECASE,
)

_SENIORITY_KEYWORDS = {
    "senior": "senior",
    "sr.": "senior",
    "sr ": "senior",
    "lead": "senior",
    "principal": "senior",
    "staff": "senior",
    "architect": "senior",
    "junior": "junior",
    "jr.": "junior",
    "jr ": "junior",
    "entry level": "junior",
    "entry-level": "junior",
    "intern": "junior",
    "fresher": "junior",
    "mid": "mid",
    "mid-level": "mid",
    "mid level": "mid",
    "associate": "mid",
}


def _split_into_sections(text: str) -> list[tuple[str, str]]:
    """Split JD into (header, content) pairs."""
    sections = []
    matches = list(_SECTION_RE.finditer(text))

    if not matches:
        return [("overview", text)]

    # Text before first section header
    if matches[0].start() > 0:
        sections.append(("overview", text[: matches[0].start()]))

    for i, m in enumerate(matches):
        header = m.group(1).lower().strip()
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        content = text[start:end].strip()
        sections.append((header, content))

    return sections


def _extract_bullet_items(text: str) -> list[str]:
    """Extract bullet/numbered list items from text."""
    items = []
    for line in text.split("\n"):
        line = line.strip()
        # Remove bullet markers
        cleaned = re.sub(r"^[\-\*\•\◦\▪\→\>\d+[\.\)]\s*", "", line).strip()
        if cleaned and len(cleaned) > 3:
            items.append(cleaned)
    return items


def _classify_skill_context(header: str) -> str:
    """Classify a section header as required, preferred, or neutral."""
    h = header.lower()
    if any(k in h for k in ["required", "must", "mandatory", "minimum", "essential", "requirement", "qualification"]):
        return "required"
    if any(k in h for k in ["preferred", "nice to have", "bonus", "desired", "good to have"]):
        return "preferred"
    return "neutral"


def analyze_jd(text: str) -> dict:
    """Extract structured intelligence from a job description.

    Returns:
        {
            "required_skills": [...],
            "preferred_skills": [...],
            "all_skills": set,
            "experience_min": int or None,
            "experience_max": int or None,
            "seniority": "junior" | "mid" | "senior" | None,
            "responsibilities": [...],
            "technologies": [...],
            "sections": {...},
        }
    """
    sections = _split_into_sections(text)
    all_skills = extract_skills(text)

    required_skills = set()
    preferred_skills = set()
    responsibilities = []
    technologies = set()

    for header, content in sections:
        context = _classify_skill_context(header)
        section_skills = extract_skills(content)

        if context == "required":
            required_skills.update(section_skills)
        elif context == "preferred":
            preferred_skills.update(section_skills)

        h = header.lower()
        if any(k in h for k in ["responsibilities", "duties", "what you"]):
            responsibilities.extend(_extract_bullet_items(content))

        if any(k in h for k in ["technologies", "tech stack", "tools"]):
            technologies.update(section_skills)

    # If no explicit required/preferred sections, treat all skills as required
    if not required_skills and not preferred_skills:
        required_skills = all_skills

    # Remove preferred from required if overlap
    preferred_skills -= required_skills
    technologies = technologies or all_skills

    # Experience level
    exp_min, exp_max = None, None
    for m in _EXPERIENCE_RE.finditer(text):
        low = int(m.group(1))
        high = int(m.group(2)) if m.group(2) else None
        if exp_min is None or low < exp_min:
            exp_min = low
        if high and (exp_max is None or high > exp_max):
            exp_max = high
    if exp_min is not None and exp_max is None:
        exp_max = exp_min + 2  # default range

    # Seniority
    seniority = None
    text_lower = text.lower()
    for keyword, level in _SENIORITY_KEYWORDS.items():
        if keyword in text_lower:
            seniority = level
            break

    return {
        "required_skills": sorted(required_skills),
        "preferred_skills": sorted(preferred_skills),
        "all_skills": all_skills,
        "experience_min": exp_min,
        "experience_max": exp_max,
        "seniority": seniority,
        "responsibilities": responsibilities[:10],
        "technologies": sorted(technologies),
        "sections": {h: c[:200] for h, c in sections},
    }
