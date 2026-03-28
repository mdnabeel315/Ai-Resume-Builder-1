"""ATS routes — /api/ats/*"""
from fastapi import APIRouter, HTTPException
from utils.models import ATSScanRequest, KeywordsRequest
from services.ats_service import run_ats_scan, extract_keywords
from services.llm_service import LLMError, LLMParseError

router = APIRouter()

@router.post("/scan")
async def scan(req: ATSScanRequest):
    try:
        return {"success": True, "data": run_ats_scan(req.resume_data, req.job_description)}
    except (LLMError, LLMParseError) as e:
        raise HTTPException(status_code=502, detail=str(e))

@router.post("/keywords")
async def keywords(req: KeywordsRequest):
    try:
        return {"success": True, "data": extract_keywords(req.job_description)}
    except (LLMError, LLMParseError) as e:
        raise HTTPException(status_code=502, detail=str(e))
