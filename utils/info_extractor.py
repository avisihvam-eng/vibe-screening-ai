"""
Candidate Info Extraction Module
Extracts name, email, phone, location, LinkedIn from resume text using regex heuristics.
"""
import re


# ── Regex Patterns ──────────────────────────────────────────────────────────────

_EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")

_PHONE_RE = re.compile(
    r"(?:\+?\d{1,3}[\s\-.]?)?"       # optional country code
    r"(?:\(?\d{2,4}\)?[\s\-.]?)?"     # optional area code
    r"\d{3,5}[\s\-.]?\d{3,5}"        # main number
)

_LINKEDIN_RE = re.compile(
    r"(?:https?://)?(?:www\.)?linkedin\.com/in/[a-zA-Z0-9\-_%]+/?",
    re.IGNORECASE,
)

_LOCATION_RE = re.compile(
    r"(?:^|\n)\s*"
    r"([A-Z][a-zA-Z\s]+,\s*[A-Z][a-zA-Z\s]+)"  # City, State / City, Country
    r"\s*(?:\n|$)",
)

_NAME_RE = re.compile(r"^([A-Z][a-z]+(?:\s[A-Z][a-z]+){1,3})$", re.MULTILINE)


# ── Extraction Functions ────────────────────────────────────────────────────────

def _extract_email(text: str) -> str:
    match = _EMAIL_RE.search(text)
    return match.group(0) if match else ""


def _extract_phone(text: str) -> str:
    # Try to find a phone number that isn't part of an email or URL
    for match in _PHONE_RE.finditer(text):
        candidate = match.group(0).strip()
        # Must have at least 7 digits to be a real phone number
        digits = re.sub(r"\D", "", candidate)
        if 7 <= len(digits) <= 15:
            return candidate
    return ""


def _extract_linkedin(text: str) -> str:
    match = _LINKEDIN_RE.search(text)
    if match:
        url = match.group(0)
        if not url.startswith("http"):
            url = "https://" + url
        return url
    # Fallback: look for "linkedin.com/in/username" style text
    simple = re.search(r"linkedin\.com/in/\S+", text, re.IGNORECASE)
    if simple:
        return "https://" + simple.group(0)
    return ""


def _extract_name(text: str) -> str:
    """Heuristic: the first line that looks like a proper name (2-4 capitalized words)."""
    # Check the first 5 non-empty lines
    lines = [ln.strip() for ln in text.split("\n") if ln.strip()][:5]
    for line in lines:
        # Skip lines that look like contact info
        if "@" in line or "linkedin" in line.lower() or re.search(r"\d{5,}", line):
            continue
        # Check if line looks like a name
        match = re.match(r"^([A-Z][a-zA-Z\.\-\']+(?:\s+[A-Z][a-zA-Z\.\-\']+){1,3})$", line)
        if match:
            return match.group(1)
    # Fallback: use _NAME_RE anywhere in the first 500 chars
    match = _NAME_RE.search(text[:500])
    return match.group(1) if match else ""


def _extract_location(text: str) -> str:
    """Heuristic: look for City, State/Country patterns in the first 500 chars."""
    match = _LOCATION_RE.search(text[:500])
    if match:
        return match.group(1).strip()
    # Fallback: look for common location indicators
    loc_indicators = re.search(
        r"(?:Location|Address|City|Based in)[:\s]+(.+)",
        text[:800],
        re.IGNORECASE,
    )
    if loc_indicators:
        return loc_indicators.group(1).strip().split("\n")[0][:60]
    return ""


# ── Main Extractor ──────────────────────────────────────────────────────────────

def extract_candidate_info(text: str) -> dict:
    """Extract structured candidate info from resume text.

    Returns:
        {
            "name": str,
            "email": str,
            "phone": str,
            "location": str,
            "linkedin": str,
        }
        Missing fields are returned as empty strings.
    """
    return {
        "name": _extract_name(text),
        "email": _extract_email(text),
        "phone": _extract_phone(text),
        "location": _extract_location(text),
        "linkedin": _extract_linkedin(text),
    }
