"""ATS Match Engine — 4-dimension semantic scoring."""

from services.llm_service import complete

_SCAN_SCHEMA = """{
  "overall_score":0,
  "breakdown":{"keyword_match":0,"skills_alignment":0,"experience_relevance":0,"title_match":0},
  "matched_keywords":[],"missing_keywords":[],"missing_skills":[],
  "strengths":[],"improvements":[{"section":"","issue":"","suggestion":""}],
  "verdict":"Strong Match | Good Match | Partial Match | Weak Match"
}"""

_KW_SCHEMA = """{
  "hard_skills":[],"soft_skills":[],"tools_and_technologies":[],
  "required_qualifications":[],"nice_to_have":[],"seniority_signals":[]
}"""


def run_ats_scan(resume_data: dict, job_description: str) -> dict:
    system = (
        "You are a senior ATS analyst.\n"
        "Score strictly:\n"
        "  keyword_match (30%): exact+semantic overlap\n"
        "  skills_alignment (35%): candidate skills vs JD requirements\n"
        "  experience_relevance (25%): past roles vs JD\n"
        "  title_match (10%): past titles vs target role\n"
        "  overall_score: weighted average of above\n"
        "Do NOT inflate. Be accurate. Return ONLY valid JSON."
    )
    user = f"RESUME:\n{resume_data}\n\nJOB DESCRIPTION:\n{job_description}\n\nReturn:\n{_SCAN_SCHEMA}"
    return complete(system, user, temperature=0.15, max_tokens=2000, json_mode=True)


def extract_keywords(job_description: str) -> dict:
    system = "You are a technical recruiter. Return ONLY valid JSON."
    user = f"Extract keywords from:\n{job_description}\n\nReturn:\n{_KW_SCHEMA}"
    return complete(system, user, temperature=0.1, max_tokens=1024, json_mode=True)


def score_label(score: int) -> str:
    if score >= 85: return "Strong Match"
    if score >= 70: return "Good Match"
    if score >= 50: return "Partial Match"
    return "Weak Match"
