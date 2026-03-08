"""
Resume Parser Module
Extracts text from PDF and DOCX files.

Uses PyPDF2 for PDFs and stdlib zipfile + xml.etree for DOCX,
avoiding lxml which is incompatible with Python 3.14 alpha.
"""
import io
import re
import zipfile
import xml.etree.ElementTree as ET
from PyPDF2 import PdfReader


# ── DOCX text extraction via stdlib ─────────────────────────────────────────────

_WORD_NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def _extract_docx_paragraphs(file_bytes: bytes) -> list[str]:
    """Parse word/document.xml from a DOCX zip and return paragraph texts."""
    with zipfile.ZipFile(io.BytesIO(file_bytes)) as zf:
        xml_bytes = zf.read("word/document.xml")
    root = ET.fromstring(xml_bytes)
    paragraphs: list[str] = []
    for p_elem in root.iter(f"{_WORD_NS}p"):
        texts = [t.text for t in p_elem.iter(f"{_WORD_NS}t") if t.text]
        line = "".join(texts).strip()
        if line:
            paragraphs.append(line)
    return paragraphs


# ── Public API ──────────────────────────────────────────────────────────────────

def extract_text_from_pdf(file_bytes: bytes) -> tuple[str, str | None]:
    """Extract text from a PDF file.

    Args:
        file_bytes: Raw bytes of the PDF file.

    Returns:
        (extracted_text, error_message) — error_message is None on success.
    """
    try:
        reader = PdfReader(io.BytesIO(file_bytes))
        pages = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                pages.append(text)
        full_text = "\n\n".join(pages)
        if not full_text.strip():
            return "", "PDF contained no extractable text."
        return full_text, None
    except Exception as e:
        return "", f"Failed to parse PDF: {e}"


def extract_text_from_docx(file_bytes: bytes) -> tuple[str, str | None]:
    """Extract text from a DOCX file using stdlib only (no lxml).

    Args:
        file_bytes: Raw bytes of the DOCX file.

    Returns:
        (extracted_text, error_message) — error_message is None on success.
    """
    try:
        paragraphs = _extract_docx_paragraphs(file_bytes)
        full_text = "\n".join(paragraphs)
        if not full_text.strip():
            return "", "DOCX contained no extractable text."
        return full_text, None
    except Exception as e:
        return "", f"Failed to parse DOCX: {e}"


def extract_text(file_name: str, file_bytes: bytes) -> tuple[str, str | None]:
    """Dispatch to the correct parser based on file extension.

    Args:
        file_name: Original filename (used to detect extension).
        file_bytes: Raw bytes of the file.

    Returns:
        (extracted_text, error_message)
    """
    ext = file_name.rsplit(".", 1)[-1].lower() if "." in file_name else ""
    if ext == "pdf":
        return extract_text_from_pdf(file_bytes)
    elif ext in ("docx",):
        return extract_text_from_docx(file_bytes)
    else:
        return "", f"Unsupported file type: .{ext}"
