"""
ATS Match Engine Service
========================
Deep semantic comparison of a resume against a job description.

Scoring dimensions:
  keyword_match        — exact + semantic keyword overlap  (0–100)
  skills_alignment     — candidate skills vs JD requirements (0–100)
  experience_relevance — relevance of past roles/projects   (0–100)
  title_match          — alignment of past titles to target (0–100)
  overall_score        — weighted (kw 30%, skills 35%, exp 25%, title 10%)
"""

from __future__ import annotations

import logging

from .error_handler import error_handler
from .llm_service import LLMError, complete

logger = logging.getLogger(__name__)

# ── Response schemas ───────────────────────────────────────────────────────────
_SCAN_SCHEMA = """
{
  "overall_score": 0,
  "breakdown": {
    "keyword_match": 0,
    "skills_alignment": 0,
    "experience_relevance": 0,
    "title_match": 0
  },
  "matched_keywords": [],
  "missing_keywords": [],
  "missing_skills": [],
  "strengths": [],
  "improvements": [
    {"section": "", "issue": "", "suggestion": ""}
  ],
  "verdict": "Strong Match | Good Match | Partial Match | Weak Match"
}""".strip()

_KEYWORDS_SCHEMA = """
{
  "hard_skills": [],
  "soft_skills": [],
  "tools_and_technologies": [],
  "required_qualifications": [],
  "nice_to_have": [],
  "seniority_signals": []
}""".strip()


# ── Public API ─────────────────────────────────────────────────────────────────
@error_handler.intercept
def run_ats_scan(resume_data: dict, job_description: str) -> dict:
    """
    Run a deep ATS scan comparing resume_data against the job description.

    Returns a rich scoring breakdown with actionable improvement suggestions.

    Raises:
        LLMError: If the Gemini call fails after retries.
    """
    if not job_description or len(job_description.strip()) < 50:
        raise ValueError("Job description must be at least 50 characters.")

    system = (
        "You are a senior ATS analyst and technical recruiter.\n"
        "Scoring rules:\n"
        "  - keyword_match: exact + semantic keyword overlap (0–100)\n"
        "  - skills_alignment: candidate skills vs JD requirements (0–100)\n"
        "  - experience_relevance: relevance of past roles/projects to JD (0–100)\n"
        "  - title_match: alignment of past job titles with target role (0–100)\n"
        "  - overall_score: weighted avg (kw 30%, skills 35%, exp 25%, title 10%)\n"
        "Be strict and accurate — do NOT inflate scores.\n"
        "Return ONLY a valid JSON object matching the schema. "
        "No markdown fences, no commentary."
    )
    user = (
        f"RESUME DATA:\n{resume_data}\n\n"
        f"JOB DESCRIPTION:\n{job_description}\n\n"
        f"Return JSON matching this schema:\n{_SCAN_SCHEMA}"
    )

    try:
        result = complete(
            system, user, temperature=0.15, max_tokens=2000, json_mode=True
        )
        logger.info(
            "ATS scan complete — overall_score=%s verdict=%s",
            result.get("overall_score"),
            result.get("verdict"),
        )
        return result
    except LLMError:
        raise
    except Exception as exc:
        raise LLMError(f"ATS scan failed: {exc}") from exc


@error_handler.intercept
def extract_keywords(job_description: str) -> dict:
    """
    Extract structured keyword categories from a job description.

    Useful for the UI keyword-highlight feature.

    Raises:
        LLMError: If the Gemini call fails after retries.
    """
    if not job_description or len(job_description.strip()) < 50:
        raise ValueError("Job description must be at least 50 characters.")

    system = (
        "You are a technical recruiter extracting structured requirements "
        "from a job description.\n"
        "Return ONLY a valid JSON object. No markdown, no commentary."
    )
    user = (
        f"Extract all keywords from this job description:\n{job_description}\n\n"
        f"Return JSON matching this schema:\n{_KEYWORDS_SCHEMA}"
    )

    try:
        return complete(
            system, user, temperature=0.1, max_tokens=1024, json_mode=True
        )
    except LLMError:
        raise
    except Exception as exc:
        raise LLMError(f"Keyword extraction failed: {exc}") from exc


def score_label(score: int) -> str:
    """Map a numeric ATS score (0–100) to a human-readable label."""
    if score >= 85:
        return "🟢 Strong Match"
    elif score >= 70:
        return "🟡 Good Match"
    elif score >= 50:
        return "🟠 Partial Match"
    else:
        return "🔴 Weak Match"
