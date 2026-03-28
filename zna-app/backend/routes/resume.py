"""Resume routes — /api/resume/*"""
from fastapi import APIRouter, HTTPException
from utils.models import ParseRequest, ParseAndGenerateRequest, GenerateResumeRequest
from services.resume_service import parse_raw_data, generate_resume, parse_and_generate
from services.llm_service import LLMError, LLMParseError

router = APIRouter()

@router.post("/parse")
async def parse(req: ParseRequest):
    try:
        data = parse_raw_data(req.raw_text)
        return {"success": True, "data": data}
    except (LLMError, LLMParseError) as e:
        raise HTTPException(status_code=502, detail=str(e))

@router.post("/generate")
async def generate(req: GenerateResumeRequest):
    try:
        data = generate_resume(req.parsed_data, req.target_job_title, req.template_style)
        return {"success": True, "data": data}
    except (LLMError, LLMParseError) as e:
        raise HTTPException(status_code=502, detail=str(e))

@router.post("/parse-and-generate")
async def parse_and_gen(req: ParseAndGenerateRequest):
    try:
        overrides = {k: v for k, v in {
            "name": req.name, "email": req.email, "phone": req.phone,
            "github": req.github, "linkedin": req.linkedin,
        }.items() if v}
        parsed, resume = parse_and_generate(
            req.raw_text, req.target_job_title, req.template_style, overrides
        )
        return {"success": True, "data": {"parsed": parsed, "resume": resume}}
    except (LLMError, LLMParseError) as e:
        raise HTTPException(status_code=502, detail=str(e))
