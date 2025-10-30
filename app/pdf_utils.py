"""Utilities for working with uploaded PDF files."""
from datetime import datetime
from pathlib import Path
from typing import Dict

import pdfplumber
import streamlit as st


def save_temp_file(uploaded_file) -> Path:
    """Persist uploaded file under .tmp with a timestamped filename."""
    tmp_dir = Path(".tmp")
    tmp_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{uploaded_file.name}"
    tmp_path = tmp_dir / filename

    with open(tmp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    return tmp_path


def get_pdf_info(pdf_path: Path) -> Dict:
    """Collect basic metadata about a PDF document."""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            page_count = len(pdf.pages)
            has_text = False

            if page_count > 0:
                first_page_text = pdf.pages[0].extract_text()
                has_text = bool(first_page_text and first_page_text.strip())

            return {
                "page_count": page_count,
                "has_text": has_text,
                "success": True,
            }

    except Exception as exc:
        return {
            "page_count": 0,
            "has_text": False,
            "success": False,
            "error": f"{exc}",
        }


def read_page_preview(pdf_path: Path, page_idx: int = 0, max_chars: int = 300) -> str:
    """Read a trimmed text preview from a specific page."""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            if page_idx >= len(pdf.pages):
                return "Page index out of range."

            page_text = pdf.pages[page_idx].extract_text()
            if not page_text or not page_text.strip():
                return "No extractable text on page 1."

            cleaned_text = " ".join(page_text.strip().split())
            if len(cleaned_text) <= max_chars:
                return cleaned_text
            return f"{cleaned_text[:max_chars]}..."

    except Exception as exc:
        return f"Error reading page preview: {exc}"


def extract_full_pdf_text(pdf_path: Path) -> str:
    """Extract the entire PDF text as a single string."""
    try:
        full_text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                full_text += page_text + "\n\n"
        return full_text.strip()
    except Exception as exc:
        st.error(f"Error extracting PDF text: {exc}")
        return ""


def format_file_size(size_bytes: int) -> str:
    """Format raw byte counts into a friendly string."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    if size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    return f"{size_bytes / (1024 * 1024):.1f} MB"
