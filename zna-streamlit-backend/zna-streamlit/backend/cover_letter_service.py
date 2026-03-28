"""
Cover Letter Service
====================
Generates tone-aware, personalised cover letters anchored to a
candidate's resume and a specific job description.

Available tones:
    Professional  — Formal, confident, achievement-driven.
    Enthusiastic  — Warm, energetic, shows personality.
    Concise       — 3 tight paragraphs. Every sentence earns its place.
"""

from __future__ import annotations

import logging
from datetime import date

from .error_handler import error_handler
from .llm_service import LLMError, complete

logger = logging.getLogger(__name__)

TONES = ["Professional", "Enthusiastic", "Concise"]

_TONE_GUIDES: dict[str, str] = {
    "Professional": (
        "Formal, confident, achievement-driven. No fluff or filler phrases."
    ),
    "Enthusiastic": (
        "Warm, energetic, genuinely excited about the role. "
        "Show personality without being unprofessional."
    ),
    "Concise": (
        "3 tight paragraphs maximum. "
        "Every sentence must earn its place — no padding."
    ),
}


@error_handler.intercept
def generate_cover_letter(
    resume_data: dict,
    job_description: str,
    tone: str = "Professional",
) -> dict:
    """
    Generate a tailored cover letter from resume data and a job description.

    Args:
        resume_data:     The structured resume dict (output of generate_resume).
        job_description: The full job description text.
        tone:            One of TONES.

    Returns:
        {
            "text":       str,   # full letter body
            "word_count": int,
            "tone":       str,
            "date":       str,   # formatted today's date
        }

    Raises:
        LLMError: If the Gemini call fails after retries.
        ValueError: If job_description is too short.
    """
    if not job_description or len(job_description.strip()) < 50:
        raise ValueError("Job description must be at least 50 characters.")

    tone_guide = _TONE_GUIDES.get(tone, _TONE_GUIDES["Professional"])

    system = (
        f"You are an elite cover letter writer.\n"
        f"Tone: {tone_guide}\n"
        "Hard rules:\n"
        "  - NEVER open with 'I am writing to apply for...'\n"
        "  - Lead with a specific, compelling hook about the role or company\n"
        "  - Reference at least 2 concrete, quantified achievements from the resume\n"
        "  - Close with a confident, non-desperate call to action\n"
        "  - Maximum 350 words\n"
        "  - Return ONLY the letter body — no subject line, no date, no metadata."
    )

    name = resume_data.get("name", "the applicant")
    exp_preview = resume_data.get("experience", [])[:2]
    skills_preview = resume_data.get("skills", {})

    user = (
        f"Write a cover letter for:\n"
        f"Applicant: {name}\n"
        f"Recent Experience: {exp_preview}\n"
        f"Skills: {skills_preview}\n\n"
        f"JOB DESCRIPTION:\n{job_description}"
    )

    try:
        text = complete(
            system,
            user,
            temperature=0.75,
            max_tokens=700,
            json_mode=False,
            use_cache=False,  # always fresh — creative generation
        )
    except LLMError:
        raise
    except Exception as exc:
        raise LLMError(f"Cover letter generation failed: {exc}") from exc

    logger.info("Cover letter generated — tone=%s words=%d", tone, len(text.split()))

    return {
        "text": text,
        "word_count": len(text.split()),
        "tone": tone,
        "date": date.today().strftime("%B %d, %Y"),
    }
