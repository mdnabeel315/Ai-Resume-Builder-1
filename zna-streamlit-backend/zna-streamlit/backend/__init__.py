"""
ZNA Backend — Public API surface.

Import from here in Streamlit pages:

    from backend import parse_and_generate, run_ats_scan, generate_cover_letter
    from backend import generate_resume_pdf, generate_cover_letter_pdf
    from backend import extract_text, extract_keywords, score_label
    from backend import TEMPLATE_STYLES, TONES
    from backend import LLMError, LLMParseError
"""

import logging

from .ats_service import extract_keywords, run_ats_scan, score_label
from .cover_letter_service import TONES, generate_cover_letter
from .error_handler import error_handler
from .file_parser import extract_text
from .llm_service import LLMError, LLMParseError
from .pdf_service import generate_cover_letter_pdf, generate_resume_pdf
from .resume_service import (
    TEMPLATE_STYLES,
    generate_resume,
    parse_and_generate,
    parse_raw_data,
)
from .validators import ATSScanInput, CoverLetterInput, ResumeParseInput

# Configure standard logging for the backend package
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

__all__ = [
    # Resume
    "parse_raw_data",
    "generate_resume",
    "parse_and_generate",
    "TEMPLATE_STYLES",
    # ATS
    "run_ats_scan",
    "extract_keywords",
    "score_label",
    # Cover Letter
    "generate_cover_letter",
    "TONES",
    # PDF
    "generate_resume_pdf",
    "generate_cover_letter_pdf",
    # File Parser
    "extract_text",
    # Validators
    "ResumeParseInput",
    "ATSScanInput",
    "CoverLetterInput",
    # Error handling
    "error_handler",
    "LLMError",
    "LLMParseError",
]
