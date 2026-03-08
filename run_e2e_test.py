"""
E2E test for V2 — runs full pipeline + verifies history save.
"""
import os, sys, time
sys.path.insert(0, os.path.dirname(__file__))

from utils.resume_parser import extract_text
from utils.info_extractor import extract_candidate_info
from utils.chunker import chunk_text
from utils.embedder import get_embeddings, load_model
from utils.scorer import score_candidate, filter_and_rank
from utils.exporter import export_to_excel, export_to_csv
from utils.skill_matcher import extract_skills, match_skills
from utils.history_store import save_session, load_all_sessions, load_session

TEST_DIR = os.path.join(os.path.dirname(__file__), "test_data")
THRESHOLD = 40

def main():
    print("=" * 60)
    print("  AutoResume Filter V2 - E2E Test")
    print("=" * 60)

    # Load JD
    with open(os.path.join(TEST_DIR, "JD.txt"), "r", encoding="utf-8") as f:
        jd_text = f.read()
    print(f"\n[1/6] JD loaded ({len(jd_text)} chars)")

    # Load model + embed JD
    print("[2/6] Loading model...")
    t0 = time.time()
    load_model()
    jd_embedding = get_embeddings([jd_text])
    jd_skills = extract_skills(jd_text)
    print(f"      Done in {time.time()-t0:.1f}s | {len(jd_skills)} JD skills found")

    # Process resumes
    print("[3/6] Processing resumes...")
    files = sorted(f for f in os.listdir(TEST_DIR) if f.endswith((".pdf",".docx")))
    candidates, failed = [], []

    for i, fname in enumerate(files, 1):
        with open(os.path.join(TEST_DIR, fname), "rb") as f:
            fb = f.read()
        text, err = extract_text(fname, fb)
        if err:
            failed.append((fname, err))
            continue
        info = extract_candidate_info(text)
        chunks = chunk_text(text)
        if not chunks:
            failed.append((fname, "Too short"))
            continue
        score = score_candidate(jd_embedding, chunks)
        sk = match_skills(jd_skills, text)
        candidates.append({
            "name": info["name"], "email": info["email"],
            "phone": info["phone"], "location": info["location"],
            "linkedin": info["linkedin"], "match_score": score,
            "matched_skills": sk["matched"], "missing_skills": sk["missing"],
            "notes": "", "source_file": fname,
        })
        status = "PASS" if score >= THRESHOLD else "FAIL"
        print(f"  {status} {fname:40s} {score:5.1f}% | {len(sk['matched'])} matched, {len(sk['missing'])} missing")

    # Filter
    print(f"\n[4/6] Filtering at >= {THRESHOLD}%...")
    qualified = filter_and_rank(candidates, threshold=THRESHOLD)

    # Save session
    print("[5/6] Saving to history...")
    sid = save_session(jd_text, THRESHOLD, candidates, failed)
    print(f"      Session: {sid}")

    # Verify history
    sessions = load_all_sessions()
    loaded = load_session(sid)
    assert loaded is not None, "Failed to load session!"
    assert len(loaded["candidates"]) == len(candidates)
    print(f"      History verified: {len(sessions)} total session(s)")

    # Export
    print("[6/6] Exporting...")
    if qualified:
        excel = export_to_excel(qualified)
        csv = export_to_csv(qualified)
        print(f"      Excel: {len(excel):,} bytes | CSV: {len(csv):,} chars")

    print(f"\n{'='*60}")
    print(f"  RESULTS: {len(qualified)} qualified / {len(candidates)} parsed / {len(failed)} failed")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
