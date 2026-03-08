"""
Session History Store
Persists screening sessions to local JSON files.
Each session = one JSON file in ~/.autoresume_filter/sessions/
"""
import json
import os
import uuid
from datetime import datetime

STORE_DIR = os.path.join(os.path.expanduser("~"), ".autoresume_filter", "sessions")


def _ensure_dir():
    os.makedirs(STORE_DIR, exist_ok=True)


def save_session(
    jd_text: str,
    threshold: float,
    candidates: list[dict],
    failed_files: list[tuple[str, str]],
) -> str:
    """Save a screening session and return the session_id."""
    _ensure_dir()
    session_id = uuid.uuid4().hex[:12]

    # Auto-extract JD title from first non-empty line
    lines = [ln.strip() for ln in jd_text.split("\n") if ln.strip()]
    jd_title = lines[0][:80] if lines else "Untitled JD"

    data = {
        "session_id": session_id,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "jd_title": jd_title,
        "jd_text": jd_text,
        "threshold": threshold,
        "total_resumes": len(candidates) + len(failed_files),
        "qualified_count": sum(
            1 for c in candidates if c.get("match_score", 0) >= threshold
        ),
        "candidates": candidates,
        "failed_files": [{"file": f, "reason": r} for f, r in failed_files],
    }

    path = os.path.join(STORE_DIR, f"{session_id}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return session_id


def load_all_sessions() -> list[dict]:
    """Load all sessions (metadata only, no candidate details). Newest first."""
    _ensure_dir()
    sessions = []
    for fname in os.listdir(STORE_DIR):
        if not fname.endswith(".json"):
            continue
        path = os.path.join(STORE_DIR, fname)
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            sessions.append({
                "session_id": data["session_id"],
                "timestamp": data["timestamp"],
                "jd_title": data["jd_title"],
                "threshold": data["threshold"],
                "total_resumes": data["total_resumes"],
                "qualified_count": data["qualified_count"],
            })
        except (json.JSONDecodeError, KeyError):
            continue
    sessions.sort(key=lambda s: s["timestamp"], reverse=True)
    return sessions


def load_session(session_id: str) -> dict | None:
    """Load full session data by ID."""
    path = os.path.join(STORE_DIR, f"{session_id}.json")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def delete_session(session_id: str) -> bool:
    """Delete a session. Returns True if deleted."""
    path = os.path.join(STORE_DIR, f"{session_id}.json")
    if os.path.exists(path):
        os.remove(path)
        return True
    return False


def update_candidate_notes(session_id: str, email: str, notes: str):
    """Update notes for a specific candidate in a session."""
    data = load_session(session_id)
    if not data:
        return
    for c in data.get("candidates", []):
        if c.get("email", "").lower() == email.lower():
            c["notes"] = notes
            break
    path = os.path.join(STORE_DIR, f"{session_id}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
