"""
Risk Signal Detector
Identifies potential red flags in candidate profiles using heuristic rules.
No LLM needed.
"""


def detect_risks(
    resume_profile: dict,
    jd_analysis: dict,
) -> list[dict]:
    """Detect risk signals in a candidate profile.

    Args:
        resume_profile: Output from resume_analyzer.analyze_resume()
        jd_analysis: Output from jd_analyzer.analyze_jd()

    Returns:
        List of {"signal": str, "severity": "low"|"medium"|"high", "detail": str}
    """
    risks = []

    # ── 1. Job Hopping ──────────────────────────────────────────────────────
    date_ranges = resume_profile.get("date_ranges", [])
    companies = resume_profile.get("companies", [])

    if len(date_ranges) >= 3:
        # Check if many short stints
        short_stints = 0
        for start, end in date_ranges:
            if start and end and (end - start) <= 1:
                short_stints += 1
        if short_stints >= 3:
            risks.append({
                "signal": "Frequent job changes",
                "severity": "medium",
                "detail": f"{short_stints} roles lasting 1 year or less",
            })
    elif len(companies) >= 4:
        risks.append({
            "signal": "Multiple employers",
            "severity": "low",
            "detail": f"{len(companies)} companies listed — worth checking tenure",
        })

    # ── 2. Career Gaps ──────────────────────────────────────────────────────
    if len(date_ranges) >= 2:
        sorted_ranges = sorted(
            [(s, e) for s, e in date_ranges if s and e],
            key=lambda x: x[0],
        )
        for i in range(len(sorted_ranges) - 1):
            end_prev = sorted_ranges[i][1]
            start_next = sorted_ranges[i + 1][0]
            gap = start_next - end_prev
            if gap >= 2:
                risks.append({
                    "signal": "Career gap detected",
                    "severity": "medium",
                    "detail": f"~{gap} year gap between roles",
                })
                break  # only flag the first gap

    # ── 3. Low Experience vs JD ─────────────────────────────────────────────
    candidate_years = resume_profile.get("experience_years")
    jd_min = jd_analysis.get("experience_min")

    if candidate_years is not None and jd_min is not None:
        if candidate_years < jd_min:
            shortfall = jd_min - candidate_years
            severity = "high" if shortfall >= 3 else "medium" if shortfall >= 1 else "low"
            risks.append({
                "signal": "Below experience requirement",
                "severity": severity,
                "detail": f"Candidate has ~{candidate_years:.0f} yrs, JD asks for {jd_min}+ yrs",
            })

    # ── 4. Skill Inflation ──────────────────────────────────────────────────
    candidate_skills = resume_profile.get("skills", [])
    if len(candidate_skills) > 25:
        risks.append({
            "signal": "Possible skill inflation",
            "severity": "low",
            "detail": f"{len(candidate_skills)} skills listed — unusually high, verify depth",
        })

    # ── 5. No LinkedIn ──────────────────────────────────────────────────────
    if not resume_profile.get("has_linkedin", False):
        risks.append({
            "signal": "No LinkedIn profile",
            "severity": "low",
            "detail": "No LinkedIn URL found — harder to verify background",
        })

    # ── 6. No Education ─────────────────────────────────────────────────────
    education = resume_profile.get("education", [])
    if not education:
        risks.append({
            "signal": "No education listed",
            "severity": "low",
            "detail": "No degree or education info detected in resume",
        })

    # ── 7. Seniority Mismatch ───────────────────────────────────────────────
    jd_seniority = jd_analysis.get("seniority")
    if jd_seniority and candidate_years is not None:
        if jd_seniority == "senior" and candidate_years < 4:
            risks.append({
                "signal": "Seniority mismatch",
                "severity": "medium",
                "detail": f"JD requires Senior level but candidate has ~{candidate_years:.0f} yrs",
            })
        elif jd_seniority == "junior" and candidate_years and candidate_years > 6:
            risks.append({
                "signal": "Overqualified",
                "severity": "low",
                "detail": f"JD is Junior level but candidate has ~{candidate_years:.0f} yrs",
            })

    return risks
