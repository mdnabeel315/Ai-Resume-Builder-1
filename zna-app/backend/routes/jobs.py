"""Job Portal routes — /api/jobs/*"""
from fastapi import APIRouter, HTTPException
from utils.models import JobStrategyRequest
from services.llm_service import complete, LLMError

router = APIRouter()

@router.post("/strategy")
async def strategy(req: JobStrategyRequest):
    system = "You are a job search strategist. Return ONLY valid JSON."
    user = f"""Generate a job search strategy for:
Role: {req.target_job_title}
Skills: {", ".join(req.skills[:15])}

Return JSON:
{{
  "linkedin_search_url": "https://www.linkedin.com/jobs/search/?keywords=...",
  "recommended_search_terms": [],
  "alternative_job_titles": [],
  "top_companies_to_target": [{{"name": "", "reason": ""}}],
  "salary_range": {{"india_lpa": "", "us_usd": "", "uk_gbp": ""}},
  "search_tips": [],
  "certifications_to_boost_profile": []
}}"""
    try:
        data = complete(system, user, temperature=0.3, max_tokens=1500, json_mode=True)
        return {"success": True, "data": data}
    except LLMError as e:
        raise HTTPException(status_code=502, detail=str(e))
