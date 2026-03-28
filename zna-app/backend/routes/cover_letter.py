"""Cover letter routes — /api/cover-letter/*"""
from fastapi import APIRouter, HTTPException
from utils.models import CoverLetterRequest
from services.cover_letter_service import generate_cover_letter
from services.llm_service import LLMError

router = APIRouter()

@router.post("/generate")
async def generate(req: CoverLetterRequest):
    try:
        return {"success": True, "data": generate_cover_letter(req.resume_data, req.job_description, req.tone)}
    except LLMError as e:
        raise HTTPException(status_code=502, detail=str(e))
