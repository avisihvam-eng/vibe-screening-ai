"""
Excel & CSV Export Module
Exports shortlisted candidates with skill gap data.
"""
import io
import pandas as pd


def _build_dataframe(candidates: list[dict]) -> pd.DataFrame:
    """Build a DataFrame from candidate dicts."""
    rows = []
    for c in candidates:
        rows.append({
            "Name": c.get("name") or "N/A",
            "Email": c.get("email") or "N/A",
            "Phone": c.get("phone") or "N/A",
            "Location": c.get("location") or "N/A",
            "LinkedIn": c.get("linkedin") or "N/A",
            "Match Score (%)": c.get("match_score", 0),
            "Matched Skills": ", ".join(c.get("matched_skills", [])),
            "Missing Skills": ", ".join(c.get("missing_skills", [])),
            "Notes": c.get("notes", ""),
        })
    df = pd.DataFrame(rows)
    df = df.sort_values("Match Score (%)", ascending=False).reset_index(drop=True)
    return df


def export_to_excel(candidates: list[dict]) -> bytes:
    """Export candidate list to an Excel file in memory.

    Args:
        candidates: List of candidate dicts (already filtered & ranked).

    Returns:
        Excel file as bytes.
    """
    df = _build_dataframe(candidates)

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Shortlisted Candidates")

        # Auto-adjust column widths
        worksheet = writer.sheets["Shortlisted Candidates"]
        for i, col in enumerate(df.columns):
            max_len = max(
                df[col].astype(str).map(len).max(),
                len(col),
            ) + 3
            worksheet.column_dimensions[chr(65 + i)].width = min(max_len, 50)

    return buffer.getvalue()


def export_to_csv(candidates: list[dict]) -> str:
    """Export candidate list to CSV string.

    Args:
        candidates: List of candidate dicts.

    Returns:
        CSV content as a string.
    """
    df = _build_dataframe(candidates)
    return df.to_csv(index=False)
