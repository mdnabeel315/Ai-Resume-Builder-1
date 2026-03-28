"""
Validators — Pydantic v2 input models for all backend services.

Prevents malformed or malicious data from reaching LLM / PDF services.
Each model is lean: just constraints, normalisation, and content checks.
"""

from __future__ import annotations

import re
from typing import Any, Dict

from pydantic import BaseModel, Field, field_validator


# ── Resume parsing / generation ────────────────────────────────────────────────
class ResumeParseInput(BaseModel):
    """Validated input for parse_raw_data() and parse_and_generate()."""

    raw_text: str = Field(..., min_length=50, max_length=12_000)
    target_job_title: str = Field(default="", max_length=120)
    template_style: str = Field(
        default="Standard Corporate",
        pattern=r"^(Standard Corporate|Modern Creative|Minimal Clean)$",
    )
    overrides: Dict[str, str] = Field(default_factory=dict)

    @field_validator("raw_text")
    @classmethod
    def must_contain_resume_content(cls, v: str) -> str:
        """Reject text that looks nothing like a resume."""
        if not re.search(
            r"(experience|education|skill|project|python|engineer|data|"
            r"work|university|college|developer|manager|intern|degree)",
            v.lower(),
        ):
            raise ValueError(
                "The pasted text does not appear to contain resume content. "
                "Please include your experience, education, or skills."
            )
        return v

    @field_validator("target_job_title")
    @classmethod
    def normalise_title(cls, v: str) -> str:
        """Strip extra whitespace and title-case the job title."""
        return " ".join(v.strip().split()).title()


# ── ATS Scanner ────────────────────────────────────────────────────────────────
class ATSScanInput(BaseModel):
    """Validated input for run_ats_scan()."""

    resume_data: Dict[str, Any]
    job_description: str = Field(..., min_length=50, max_length=6_000)


# ── Cover Letter ───────────────────────────────────────────────────────────────
class CoverLetterInput(BaseModel):
    """Validated input for generate_cover_letter()."""

    resume_data: Dict[str, Any]
    job_description: str = Field(..., min_length=50, max_length=6_000)
    tone: str = Field(
        default="Professional",
        pattern=r"^(Professional|Enthusiastic|Concise)$",
    )
