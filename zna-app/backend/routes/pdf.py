"""PDF routes — /api/pdf/*"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from utils.models import ResumePDFRequest, CoverLetterPDFRequest
from services.pdf_service import generate_resume_pdf, generate_cover_letter_pdf

router = APIRouter()

@router.post("/resume")
async def resume_pdf(req: ResumePDFRequest):
    try:
        pdf = generate_resume_pdf(req.resume_data, req.template_style)
        name = (req.resume_data.get("name") or "resume").replace(" ", "_")
        return Response(
            content=pdf, media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{name}_resume.pdf"'},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {e}")

@router.post("/cover-letter")
async def cover_letter_pdf(req: CoverLetterPDFRequest):
    try:
        pdf = generate_cover_letter_pdf(req.cover_letter)
        return Response(
            content=pdf, media_type="application/pdf",
            headers={"Content-Disposition": 'attachment; filename="cover_letter.pdf"'},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {e}")
