"""Resume Service — parse raw text + generate polished resume."""

from __future__ import annotations
from services.llm_service import complete

TEMPLATE_STYLES = ["Standard Corporate", "Modern Creative", "Minimal Clean"]

_TEMPLATE_DESC = {
    "Standard Corporate": "formal, ATS-optimised, conservative, clean section hierarchy",
    "Modern Creative":    "modern, tech-forward, bold headers, great for engineering/design",
    "Minimal Clean":      "ultra-minimal, whitespace-driven, executive tone",
}

_PARSE_SCHEMA = """{
  "name":"","email":"","phone":"","github":"","linkedin":"","summary":"",
  "skills":[],"experience":[{"title":"","company":"","duration":"","bullets":[]}],
  "education":[{"degree":"","institution":"","year":""}],
  "projects":[{"name":"","description":"","tech":[]}],"certifications":[]
}"""

_RESUME_SCHEMA = """{
  "name":"","contact":{"email":"","phone":"","github":"","linkedin":""},
  "summary":"","skills":{"technical":[],"soft":[]},
  "experience":[{"title":"","company":"","duration":"","bullets":[]}],
  "education":[{"degree":"","institution":"","year":""}],
  "projects":[{"name":"","description":"","tech":[]}],
  "certifications":[],"ats_score":0,"template_style":""
}"""


def parse_raw_data(raw_text: str) -> dict:
    system = (
        "You are an expert resume parser. Extract every piece of information present. "
        "Return ONLY a valid JSON object — no commentary, no markdown fences."
    )
    user = f"Parse into this schema:\n{_PARSE_SCHEMA}\n\nTEXT:\n{raw_text}"
    return complete(system, user, temperature=0.1, max_tokens=2048, json_mode=True)


def generate_resume(parsed: dict, target_job_title: str, template_style: str = "Standard Corporate") -> dict:
    style = _TEMPLATE_DESC.get(template_style, _TEMPLATE_DESC["Standard Corporate"])
    system = (
        f"You are a world-class resume writer. Style: {style}.\n"
        "Rules: start every bullet with a past-tense action verb; quantify achievements; "
        "mirror language from the target role; set ats_score 0-100 honestly.\n"
        "Return ONLY valid JSON — no markdown fences."
    )
    user = (
        f'Target role: "{target_job_title}"\nTemplate: "{template_style}"\n'
        f"Candidate data:\n{parsed}\n\nReturn JSON:\n{_RESUME_SCHEMA}"
    )
    return complete(system, user, temperature=0.4, max_tokens=3000, json_mode=True)


def parse_and_generate(
    raw_text: str,
    target_job_title: str,
    template_style: str = "Standard Corporate",
    overrides: dict | None = None,
) -> tuple[dict, dict]:
    parsed = parse_raw_data(raw_text)
    if overrides:
        for k, v in overrides.items():
            if v:
                parsed[k] = v
    resume = generate_resume(parsed, target_job_title, template_style)
    return parsed, resume
