"""
Resume Service
==============
Three public functions:

  parse_raw_data(raw_text)
      → Extract structured JSON from any pasted LinkedIn/resume text.

  generate_resume(parsed_data, target_job_title, template_style)
      → Produce a polished, ATS-optimised resume dict.

  parse_and_generate(raw_text, target_job_title, ...)
      → Convenience pipeline: parse → optional overrides → generate.
        Returns (parsed_data, generated_resume).
"""

from __future__ import annotations

import logging
from typing import Any

from .error_handler import error_handler
from .llm_service import LLMError, complete
from .validators import ResumeParseInput

logger = logging.getLogger(__name__)

# ── Template catalogue ─────────────────────────────────────────────────────────
TEMPLATE_STYLES = ["Standard Corporate", "Modern Creative", "Minimal Clean"]

_TEMPLATE_DESCRIPTIONS: dict[str, str] = {
    "Standard Corporate": (
        "formal, ATS-optimised, clean section hierarchy, conservative typography"
    ),
    "Modern Creative": (
        "modern, tech-forward, bold headers, ideal for design/engineering roles"
    ),
    "Minimal Clean": (
        "ultra-minimal, generous whitespace, executive tone, zero clutter"
    ),
}

# ── JSON schemas passed to the LLM ────────────────────────────────────────────
_PARSE_SCHEMA = """
{
  "name": "",
  "email": "",
  "phone": "",
  "github": "",
  "linkedin": "",
  "summary": "",
  "skills": [],
  "experience": [{"title":"","company":"","duration":"","bullets":[]}],
  "education": [{"degree":"","institution":"","year":""}],
  "projects": [{"name":"","description":"","tech":[]}],
  "certifications": []
}""".strip()

_GENERATE_SCHEMA = """
{
  "name": "",
  "contact": {"email":"","phone":"","github":"","linkedin":""},
  "summary": "",
  "skills": {"technical":[],"soft":[]},
  "experience": [{"title":"","company":"","duration":"","bullets":[]}],
  "education": [{"degree":"","institution":"","year":""}],
  "projects": [{"name":"","description":"","tech":[]}],
  "certifications": [],
  "ats_score": 0,
  "template_style": ""
}""".strip()


# ── Service functions ──────────────────────────────────────────────────────────
@error_handler.intercept
def parse_raw_data(raw_text: str) -> dict | None:
    """
    Parse any pasted resume or LinkedIn text into a structured dict.
    Uses a low temperature for maximum extraction accuracy.

    Returns:
        dict on success, None on failure (error shown in Streamlit UI).
    """
    ResumeParseInput(raw_text=raw_text)

    system = (
        "You are an expert resume parser. "
        "Extract every piece of information present. "
        "Return ONLY a valid JSON object matching the schema exactly — "
        "no commentary, no markdown fences."
    )
    user = (
        f"Parse the following text into this JSON schema:\n{_PARSE_SCHEMA}"
        f"\n\nTEXT:\n{raw_text}"
    )
    return complete(system, user, temperature=0.1, max_tokens=2048, json_mode=True)


@error_handler.intercept
def generate_resume(
    parsed_data: dict,
    target_job_title: str,
    template_style: str = "Standard Corporate",
) -> dict | None:
    """
    Generate a polished, ATS-optimised resume from structured candidate data.

    Returns:
        dict on success, None on failure (error shown in Streamlit UI).
    """
    style_desc = _TEMPLATE_DESCRIPTIONS.get(
        template_style, _TEMPLATE_DESCRIPTIONS["Standard Corporate"]
    )

    system = (
        f"You are a world-class resume writer.\n"
        f"Style: {style_desc}.\n"
        "Rules:\n"
        "- Every bullet point must open with a strong past-tense action verb\n"
        "- Quantify achievements wherever data exists (%, $, X users, N months)\n"
        "- Mirror language from the target job title naturally\n"
        "- Set ats_score to how well the resume matches the target role (0–100)\n"
        "Return ONLY a valid JSON object — no markdown fences, no commentary."
    )
    user = (
        f'Target role: "{target_job_title}"\n'
        f'Template style: "{template_style}"\n\n'
        f"Candidate data:\n{parsed_data}\n\n"
        f"Return JSON matching this schema:\n{_GENERATE_SCHEMA}"
    )
    return complete(system, user, temperature=0.4, max_tokens=3000, json_mode=True)


def parse_and_generate(
    raw_text: str,
    target_job_title: str,
    template_style: str = "Standard Corporate",
    overrides: dict[str, Any] | None = None,
) -> tuple[dict, dict]:
    """
    Convenience pipeline: parse → optional field overrides → generate.

    Args:
        raw_text:         Pasted LinkedIn / resume text.
        target_job_title: The role the candidate is applying for.
        template_style:   One of TEMPLATE_STYLES.
        overrides:        Optional dict of fields to inject after parsing
                          (e.g. {"name": "Syed Zaid", "email": "..."}).

    Returns:
        (parsed_data, generated_resume)

    Raises:
        LLMError: If either LLM call fails or returns None.
    """
    # Validate all inputs up-front
    ResumeParseInput(
        raw_text=raw_text,
        target_job_title=target_job_title,
        template_style=template_style,
    )

    parsed = parse_raw_data(raw_text)
    if parsed is None:
        raise LLMError(
            "parse_raw_data returned None — the LLM call failed. "
            "Check your Gemini API key and the error shown above."
        )

    # Apply any explicit form-field overrides before generation
    if overrides:
        for field, value in overrides.items():
            if value:  # ignore empty strings
                parsed[field] = value

    resume = generate_resume(parsed, target_job_title, template_style)
    if resume is None:
        raise LLMError(
            "generate_resume returned None — the LLM call failed. "
            "Check your Gemini API key and the error shown above."
        )

    logger.info(
        "Resume pipeline complete — ats_score=%s template=%s",
        resume.get("ats_score", "N/A"),
        template_style,
    )
    return parsed, resume
