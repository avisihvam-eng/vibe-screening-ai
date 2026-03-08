"""
Scoring & Ranking Module
Computes semantic match scores and filters/ranks candidates.
"""
import numpy as np
from utils.embedder import get_embeddings, cosine_similarity


def score_candidate(
    jd_embedding: np.ndarray,
    chunk_texts: list[str],
) -> float:
    """Compute a candidate's semantic match score against the JD.

    Strategy: embed all resume chunks, compute cosine similarity of each
    chunk against the JD, take the average of the top-5 similarities, and
    normalize to 0–100.

    Args:
        jd_embedding: Shape (1, d) — the JD embedding.
        chunk_texts: List of resume text chunks for this candidate.

    Returns:
        Match score as a float in [0, 100].
    """
    if not chunk_texts:
        return 0.0

    chunk_embeddings = get_embeddings(chunk_texts)  # (n, d)
    sims = cosine_similarity(jd_embedding, chunk_embeddings)  # (1, n)
    sims_flat = sims.flatten()

    # Average top-5 (or fewer if candidate has < 5 chunks)
    top_k = min(5, len(sims_flat))
    top_sims = np.sort(sims_flat)[-top_k:]
    avg_sim = float(np.mean(top_sims))

    # Clamp to [0, 1] then convert to percentage
    score = max(0.0, min(1.0, avg_sim)) * 100
    return round(score, 2)


def filter_and_rank(
    candidates: list[dict],
    threshold: float = 40.0,
) -> list[dict]:
    """Filter candidates at or above the threshold and sort descending.

    Args:
        candidates: List of dicts, each must contain a "match_score" key.
        threshold: Minimum match score (0–100) to qualify.

    Returns:
        Filtered and sorted list (highest score first).
    """
    qualified = [c for c in candidates if c.get("match_score", 0) >= threshold]

    # Remove duplicates by email (keep highest score)
    seen_emails: dict[str, dict] = {}
    for c in qualified:
        email = c.get("email", "").lower().strip()
        if email and email in seen_emails:
            if c["match_score"] > seen_emails[email]["match_score"]:
                seen_emails[email] = c
        elif email:
            seen_emails[email] = c
        else:
            # No email — can't dedup, keep it
            seen_emails[id(c)] = c

    deduped = list(seen_emails.values())
    deduped.sort(key=lambda c: c["match_score"], reverse=True)
    return deduped
