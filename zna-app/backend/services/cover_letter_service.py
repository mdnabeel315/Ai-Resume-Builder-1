"""Cover Letter Service — tone-aware, quantified, ATS-aligned."""

from datetime import date
from services.llm_service import complete

TONES = ["Professional", "Enthusiastic", "Concise"]

_TONE = {
    "Professional":   "Formal, confident, achievement-driven. No filler.",
    "Enthusiastic":   "Warm, energetic, genuinely excited. Show personality.",
    "Concise":        "3 tight paragraphs max. Every sentence earns its place.",
}


def generate_cover_letter(resume_data: dict, job_description: str, tone: str = "Professional") -> dict:
    system = (
        f"You are an elite cover letter writer. Tone: {_TONE.get(tone, _TONE['Professional'])}\n"
        "Rules: never open with 'I am writing'; lead with a specific hook; "
        "reference 2+ quantified achievements; confident non-desperate close; max 350 words.\n"
        "Return ONLY the letter body — no subject, no metadata."
    )
    user = (
        f"Applicant: {resume_data.get('name','')}\n"
        f"Experience: {resume_data.get('experience', [])[:2]}\n"
        f"Skills: {resume_data.get('skills', {})}\n\n"
        f"JOB DESCRIPTION:\n{job_description}"
    )
    text = complete(system, user, temperature=0.75, max_tokens=600, json_mode=False, use_cache=False)
    return {
        "text": text,
        "word_count": len(text.split()),
        "tone": tone,
        "date": date.today().strftime("%B %d, %Y"),
        "applicant_name": resume_data.get("name", ""),
    }
