"""
Backend tests — ZNA AI Studio
Run: cd backend && pytest tests/ -v

Real LLM calls are skipped unless GEMINI_API_KEY is set.
"""

import os
import pytest
from fastapi.testclient import TestClient

# Provide a dummy key so config doesn't fail on import
os.environ.setdefault("GEMINI_API_KEY", "test-key-placeholder")

from main import app  # noqa: E402

client = TestClient(app)
HAS_REAL_KEY = os.environ.get("GEMINI_API_KEY", "test-key-placeholder") != "test-key-placeholder"


# ── Health ────────────────────────────────────────────────────────────────────
def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert "version" in data
    assert "services" in data


# ── Resume ────────────────────────────────────────────────────────────────────
def test_parse_missing_body():
    r = client.post("/api/resume/parse", json={})
    assert r.status_code == 422  # validation error


def test_parse_short_text():
    r = client.post("/api/resume/parse", json={"raw_text": "too short"})
    assert r.status_code == 422


def test_generate_missing_fields():
    r = client.post("/api/resume/generate", json={"parsed_data": {}})
    assert r.status_code == 422


def test_parse_and_generate_missing_title():
    r = client.post("/api/resume/parse-and-generate", json={
        "raw_text": "A" * 100,  # long enough to pass min_length
    })
    assert r.status_code == 422


# ── ATS ───────────────────────────────────────────────────────────────────────
def test_ats_scan_missing_fields():
    r = client.post("/api/ats/scan", json={"resume_data": {}})
    assert r.status_code == 422


def test_ats_keywords_too_short():
    r = client.post("/api/ats/keywords", json={"job_description": "hi"})
    assert r.status_code == 422


# ── Cover Letter ──────────────────────────────────────────────────────────────
def test_cover_letter_missing_jd():
    r = client.post("/api/cover-letter/generate", json={
        "resume_data": {"name": "Test"},
    })
    assert r.status_code == 422


# ── PDF ───────────────────────────────────────────────────────────────────────
def test_pdf_resume_missing_data():
    r = client.post("/api/pdf/resume", json={})
    assert r.status_code == 422


# ── Jobs ──────────────────────────────────────────────────────────────────────
def test_jobs_strategy_missing_title():
    r = client.post("/api/jobs/strategy", json={})
    assert r.status_code == 422


# ── Live LLM tests (only when real key present) ───────────────────────────────
@pytest.mark.skipif(not HAS_REAL_KEY, reason="No real GEMINI_API_KEY")
def test_parse_real():
    r = client.post("/api/resume/parse", json={
        "raw_text": (
            "John Doe | john@example.com | +1-555-0100\n"
            "Software Engineer at Acme Corp (2021-2024)\n"
            "- Built REST APIs serving 500k users\n"
            "- Led migration to microservices, reducing latency by 40%\n"
            "B.Tech Computer Science, MIT, 2021\n"
            "Skills: Python, FastAPI, React, AWS, Docker, PostgreSQL"
        )
    })
    assert r.status_code == 200
    data = r.json()
    assert data["success"] is True
    assert "name" in data["data"]


@pytest.mark.skipif(not HAS_REAL_KEY, reason="No real GEMINI_API_KEY")
def test_ats_scan_real():
    resume = {
        "name": "Jane Smith",
        "skills": {"technical": ["Python", "React", "AWS"], "soft": ["Leadership"]},
        "experience": [{"title": "Backend Engineer", "company": "TechCo", "duration": "2022-2024", "bullets": ["Built APIs"]}],
    }
    jd = (
        "We are looking for a Backend Engineer with strong Python and AWS skills. "
        "Experience with React is a plus. Must have 2+ years of API development experience. "
        "Strong communication and leadership skills required."
    )
    r = client.post("/api/ats/scan", json={"resume_data": resume, "job_description": jd})
    assert r.status_code == 200
    data = r.json()
    assert data["success"] is True
    assert 0 <= data["data"]["overall_score"] <= 100
