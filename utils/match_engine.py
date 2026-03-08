"""
Match Engine Module
Multi-factor composite scoring with explanations.
No LLM — uses embeddings + skill matching + heuristics.
"""


def compute_composite_score(
    semantic_score: float,
    matched_skills: list[str],
    missing_skills: list[str],
    candidate_years: float | None,
    jd_exp_min: int | None,
    jd_exp_max: int | None,
    jd_seniority: str | None,
    candidate_skills_count: int = 0,
) -> dict:
    """Compute a weighted composite match score.

    Weights:
        - Semantic match: 40%
        - Skill match: 30%
        - Experience match: 15%
        - Seniority match: 15%

    Returns:
        {
            "composite_score": float (0-100),
            "semantic_score": float,
            "skill_score": float,
            "experience_score": float,
            "seniority_score": float,
            "breakdown": {...},
        }
    """
    # ── Skill Score (0-100) ──────────────────────────────────────────────────
    total_jd_skills = len(matched_skills) + len(missing_skills)
    if total_jd_skills > 0:
        skill_score = (len(matched_skills) / total_jd_skills) * 100
    else:
        skill_score = 50.0  # neutral if no skills detected

    # ── Experience Score (0-100) ─────────────────────────────────────────────
    if candidate_years is not None and jd_exp_min is not None:
        if candidate_years >= jd_exp_min:
            # At or above minimum → high score
            if jd_exp_max and candidate_years > jd_exp_max + 3:
                experience_score = 75.0  # overqualified slightly penalized
            else:
                experience_score = 100.0
        else:
            # Below minimum → proportional score
            ratio = candidate_years / jd_exp_min if jd_exp_min > 0 else 0
            experience_score = min(100, ratio * 100)
    else:
        experience_score = 50.0  # neutral if can't determine

    # ── Seniority Score (0-100) ──────────────────────────────────────────────
    if jd_seniority and candidate_years is not None:
        level_map = {"junior": (0, 3), "mid": (2, 6), "senior": (5, 99)}
        low, high = level_map.get(jd_seniority, (0, 99))
        if low <= candidate_years <= high:
            seniority_score = 100.0
        elif candidate_years < low:
            seniority_score = max(20, (candidate_years / low) * 100) if low > 0 else 50
        else:
            seniority_score = 75.0  # overqualified
    else:
        seniority_score = 50.0  # neutral

    # ── Composite ────────────────────────────────────────────────────────────
    composite = (
        semantic_score * 0.40
        + skill_score * 0.30
        + experience_score * 0.15
        + seniority_score * 0.15
    )
    composite = round(min(100, max(0, composite)), 1)

    return {
        "composite_score": composite,
        "semantic_score": round(semantic_score, 1),
        "skill_score": round(skill_score, 1),
        "experience_score": round(experience_score, 1),
        "seniority_score": round(seniority_score, 1),
    }


def generate_explanation(
    name: str,
    matched_skills: list[str],
    missing_skills: list[str],
    candidate_years: float | None,
    jd_exp_min: int | None,
    risks: list[dict],
    companies: list[str],
    education: list[str],
    composite: dict,
) -> dict:
    """Generate an explanation for a candidate's match.

    Returns:
        {
            "strengths": [...],
            "gaps": [...],
            "summary": str,
        }
    """
    strengths = []
    gaps = []

    # Strengths from skills
    if len(matched_skills) >= 5:
        top = ", ".join(matched_skills[:5])
        strengths.append(f"Strong skill alignment: {top}")
    elif matched_skills:
        strengths.append(f"Matches {len(matched_skills)} required skill(s): {', '.join(matched_skills)}")

    # Strengths from experience
    if candidate_years is not None:
        if jd_exp_min and candidate_years >= jd_exp_min:
            strengths.append(f"{candidate_years:.0f} years of experience meets the {jd_exp_min}+ year requirement")
        elif candidate_years >= 3:
            strengths.append(f"{candidate_years:.0f} years of professional experience")

    # Strengths from companies
    if companies:
        strengths.append(f"Industry experience at {', '.join(companies[:3])}")

    # Strengths from education
    if education:
        strengths.append(f"Education: {education[0]}")

    # Strengths from high semantic score
    if composite.get("semantic_score", 0) >= 70:
        strengths.append("High semantic relevance to the job description")

    # Gaps from missing skills
    if missing_skills:
        if len(missing_skills) <= 3:
            gaps.append(f"Missing skills: {', '.join(missing_skills)}")
        else:
            gaps.append(f"Missing {len(missing_skills)} required skills including: {', '.join(missing_skills[:3])}")

    # Gaps from experience
    if candidate_years is not None and jd_exp_min is not None and candidate_years < jd_exp_min:
        gaps.append(f"Experience shortfall: has {candidate_years:.0f} yrs, JD needs {jd_exp_min}+")

    # Gaps from risks
    high_risks = [r for r in risks if r["severity"] == "high"]
    if high_risks:
        for r in high_risks:
            gaps.append(f"{r['signal']}: {r['detail']}")

    # No strengths fallback
    if not strengths:
        strengths.append("Resume was processed but limited structured data was extracted")

    # Generate summary
    score = composite.get("composite_score", 0)
    if score >= 75:
        verdict = "Strong candidate — recommended for interview"
    elif score >= 55:
        verdict = "Decent fit — worth a closer look"
    elif score >= 40:
        verdict = "Partial match — consider if talent pool is limited"
    else:
        verdict = "Weak match — likely not a fit for this role"

    years_str = f" with {candidate_years:.0f} years experience" if candidate_years else ""
    top_skills = ", ".join(matched_skills[:3]) if matched_skills else "general tech"
    summary = f"{name}{years_str} in {top_skills}. {verdict}."

    return {
        "strengths": strengths,
        "gaps": gaps,
        "summary": summary,
    }
