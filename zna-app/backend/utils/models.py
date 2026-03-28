"""Pydantic models — request validation + response typing."""

from pydantic import BaseModel, Field
from typing import Optional


# ── Resume ─────────────────────────────────────────────────────────────────────
class ParseRequest(BaseModel):
    raw_text: str = Field(..., min_length=50, description="Raw resume/LinkedIn text")

class ParseAndGenerateRequest(BaseModel):
    raw_text: str = Field(..., min_length=50)
    target_job_title: str = Field(..., min_length=2)
    template_style: str = "Standard Corporate"
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    github: Optional[str] = None
    linkedin: Optional[str] = None

class GenerateResumeRequest(BaseModel):
    parsed_data: dict
    target_job_title: str = Field(..., min_length=2)
    template_style: str = "Standard Corporate"


# ── ATS ────────────────────────────────────────────────────────────────────────
class ATSScanRequest(BaseModel):
    resume_data: dict
    job_description: str = Field(..., min_length=50)

class KeywordsRequest(BaseModel):
    job_description: str = Field(..., min_length=50)


# ── Cover Letter ───────────────────────────────────────────────────────────────
class CoverLetterRequest(BaseModel):
    resume_data: dict
    job_description: str = Field(..., min_length=50)
    tone: str = "Professional"


# ── PDF ────────────────────────────────────────────────────────────────────────
class ResumePDFRequest(BaseModel):
    resume_data: dict
    template_style: str = "Standard Corporate"

class CoverLetterPDFRequest(BaseModel):
    cover_letter: dict


# ── Jobs ───────────────────────────────────────────────────────────────────────
class JobStrategyRequest(BaseModel):
    target_job_title: str = Field(..., min_length=2)
    skills: list[str] = []


# ── Common responses ───────────────────────────────────────────────────────────
class SuccessResponse(BaseModel):
    success: bool = True
    data: dict | list | None = None

class ErrorResponse(BaseModel):
    success: bool = False
    error: str
