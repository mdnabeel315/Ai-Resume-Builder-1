"""
File Parser — Extract clean text from uploaded PDF and DOCX resumes.
Feeds directly into resume_service.parse_raw_data().
"""

from __future__ import annotations

import io
import logging
from typing import Union

import fitz  # PyMuPDF
from docx import Document

logger = logging.getLogger(__name__)


def extract_text(file_bytes: bytes, mime_type: str) -> str:
    """
    Extract clean plain text from an uploaded resume file.

    Args:
        file_bytes: Raw bytes from st.file_uploader.getvalue().
        mime_type:  MIME type string — 'application/pdf' or the DOCX MIME type.

    Returns:
        Concatenated clean text ready for LLM parsing.

    Raises:
        ValueError: If the MIME type is not supported.
        Exception:  Propagated from the underlying parser on read errors.
    """
    if not file_bytes:
        raise ValueError("File bytes are empty — nothing to parse.")

    mime = mime_type.lower()
    if "pdf" in mime:
        return _extract_pdf(file_bytes)
    elif "document" in mime or "docx" in mime or "word" in mime:
        return _extract_docx(file_bytes)
    else:
        raise ValueError(
            f"Unsupported file type: '{mime_type}'. "
            "Only PDF and DOCX files are supported."
        )


# ── Private helpers ────────────────────────────────────────────────────────────
def _extract_pdf(file_bytes: bytes) -> str:
    """Extract text from a PDF using PyMuPDF (fitz)."""
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        pages: list[str] = []
        for page in doc:
            text = page.get_text("text")
            if text.strip():
                pages.append(text)
        doc.close()

        full_text = "\n".join(pages).strip()
        if not full_text:
            raise ValueError(
                "No readable text found in this PDF. "
                "It may be image-only (scanned). "
                "Please copy and paste your text manually instead."
            )

        logger.info("PDF parsed — %d chars extracted", len(full_text))
        return full_text

    except ValueError:
        raise
    except Exception as exc:
        logger.error("PDF extraction failed: %s", exc)
        raise RuntimeError(f"Could not read PDF: {exc}") from exc


def _extract_docx(file_bytes: bytes) -> str:
    """Extract text from a DOCX file using python-docx."""
    try:
        doc = Document(io.BytesIO(file_bytes))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        full_text = "\n".join(paragraphs).strip()

        if not full_text:
            raise ValueError(
                "No readable text found in this DOCX file. "
                "Please copy and paste your text manually instead."
            )

        logger.info("DOCX parsed — %d chars extracted", len(full_text))
        return full_text

    except ValueError:
        raise
    except Exception as exc:
        logger.error("DOCX extraction failed: %s", exc)
        raise RuntimeError(f"Could not read DOCX: {exc}") from exc
