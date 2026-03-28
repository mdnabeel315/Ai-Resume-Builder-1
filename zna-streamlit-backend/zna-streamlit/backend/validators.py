"""
Pydantic v2 validators for robust backend input handling.
Prevents malformed data from reaching LLM/PDF services.
"""

import re
from typing import Any, Dict

from pydantic import BaseModel, Field, field_validator


class ResumeParseInput(BaseModel):
    """Validated input for parse_raw_data / parse_and_generate."""

    raw_text: str = Field(..., min_length=50, max_length=10_000)
    target_job_title: str = Field(default="", max_length=100)
    template_style: str = Field(
        default="Standard Corporate",
        pattern=r"^(Standard Corporate|Modern Creative|Minimal Clean)$",
    )
    overrides: Dict[str, str] = Field(default_factory=dict)

    @field_validator("raw_text")
    @classmethod
    def check_resume_content(cls, v: str) -> str:
        if not re.search(
            r"(experience|education|skill|project|python|engineer|data|work|university|college)",
            v.lower(),
        ):
            raise ValueError("Text appears to contain no resume content.")
        return v

    @field_validator("target_job_title")
    @classmethod
    def normalize_title(cls, v: str) -> str:
        return " ".join(v.strip().split()).title()


class ATSScanInput(BaseModel):
    """Validated input for ATS scan."""

    resume_data: Dict[str, Any]
    job_description: str = Field(..., min_length=50, max_length=5_000)


class CoverLetterInput(BaseModel):
    """Validated input for cover letter generation."""

    resume_data: Dict[str, Any]
    job_description: str = Field(..., min_length=50, max_length=5_000)
    tone: str = Field(
        default="Professional",
        pattern=r"^(Professional|Enthusiastic|Concise)$",
    )
