"""
PDF Service — Professional resume + cover letter PDFs via ReportLab Platypus.
3 themed templates. Returns bytes. Bug-fixed: no duplicate section headers.
"""

from __future__ import annotations
import io
from datetime import date
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    BaseDocTemplate, Frame, PageTemplate,
    Paragraph, Spacer, HRFlowable, KeepTogether,
)

PAGE_W, PAGE_H = A4
MARGIN_H = 1.8 * cm
MARGIN_V = 1.5 * cm

THEMES: dict[str, dict] = {
    "Standard Corporate": {
        "accent": colors.HexColor("#1a365d"), "sub": colors.HexColor("#4a5568"),
        "rule": colors.HexColor("#2b6cb0"), "nsize": 22, "hsize": 9, "bsize": 9,
        "fn": "Times-Roman", "fb": "Times-Bold",
    },
    "Modern Creative": {
        "accent": colors.HexColor("#6b21a8"), "sub": colors.HexColor("#553c9a"),
        "rule": colors.HexColor("#7c3aed"), "nsize": 24, "hsize": 9, "bsize": 9,
        "fn": "Helvetica", "fb": "Helvetica-Bold",
    },
    "Minimal Clean": {
        "accent": colors.HexColor("#111827"), "sub": colors.HexColor("#6b7280"),
        "rule": colors.HexColor("#9ca3af"), "nsize": 22, "hsize": 8, "bsize": 9,
        "fn": "Helvetica", "fb": "Helvetica-Bold",
    },
}


def _safe(val: Any) -> str:
    if not val:
        return ""
    return str(val).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _build_styles(t: dict) -> dict:
    fn, fb, acc, sub = t["fn"], t["fb"], t["accent"], t["sub"]
    body_color = colors.HexColor("#2d2d2d")
    return {
        "name":    ParagraphStyle("name",    fontName=fb, fontSize=t["nsize"], textColor=acc, spaceAfter=1*mm, leading=t["nsize"]+2),
        "contact": ParagraphStyle("contact", fontName=fn, fontSize=7.5, textColor=sub, spaceAfter=3*mm, leading=11),
        "h2":      ParagraphStyle("h2",      fontName=fb, fontSize=t["hsize"], textColor=acc, spaceBefore=4*mm, spaceAfter=1*mm, leading=12),
        "eh":      ParagraphStyle("eh",      fontName=fb, fontSize=t["bsize"], textColor=colors.HexColor("#1a1a1a"), leading=13),
        "meta":    ParagraphStyle("meta",    fontName=fn, fontSize=8, textColor=sub, leading=11),
        "bullet":  ParagraphStyle("bullet",  fontName=fn, fontSize=t["bsize"], textColor=body_color, leftIndent=10, firstLineIndent=-10, leading=12, spaceAfter=1*mm),
        "body":    ParagraphStyle("body",    fontName=fn, fontSize=t["bsize"], textColor=body_color, leading=13, spaceAfter=2*mm),
    }


def _rule(t: dict) -> HRFlowable:
    return HRFlowable(width="100%", thickness=0.8, color=t["rule"], spaceAfter=2*mm)


def _section(title: str, styles: dict, theme: dict) -> list:
    return [Paragraph(title.upper(), styles["h2"]), _rule(theme)]


def _make_doc(buffer: io.BytesIO, left=MARGIN_H, right=MARGIN_H, top=MARGIN_V, bottom=MARGIN_V) -> BaseDocTemplate:
    doc = BaseDocTemplate(buffer, pagesize=A4, leftMargin=left, rightMargin=right, topMargin=top, bottomMargin=bottom)
    frame = Frame(left, bottom, PAGE_W - left - right, PAGE_H - top - bottom, id="main")
    doc.addPageTemplates([PageTemplate(id="main", frames=frame)])
    return doc


def generate_resume_pdf(resume: dict, template_style: str = "Standard Corporate") -> bytes:
    theme  = THEMES.get(template_style, THEMES["Standard Corporate"])
    styles = _build_styles(theme)
    buffer = io.BytesIO()
    doc    = _make_doc(buffer)
    story: list = []

    # Header
    contact = resume.get("contact") or {}
    story.append(Paragraph(_safe(resume.get("name", "Your Name")), styles["name"]))
    cp = "  ·  ".join(_safe(p) for p in [contact.get("email"), contact.get("phone"), contact.get("linkedin"), contact.get("github")] if p)
    if cp:
        story.append(Paragraph(cp, styles["contact"]))
    story.append(_rule(theme))

    # Summary
    if resume.get("summary"):
        story += _section("Summary", styles, theme)
        story.append(Paragraph(_safe(resume["summary"]), styles["body"]))

    # Skills
    skills = resume.get("skills") or {}
    tech, soft = skills.get("technical") or [], skills.get("soft") or []
    if tech or soft:
        story += _section("Skills", styles, theme)
        if tech: story.append(Paragraph(f'<b>Technical:</b>  {_safe(", ".join(tech))}', styles["body"]))
        if soft: story.append(Paragraph(f'<b>Soft Skills:</b>  {_safe(", ".join(soft))}', styles["body"]))

    # Experience
    experience = resume.get("experience") or []
    if experience:
        story += _section("Experience", styles, theme)
        for exp in experience:
            block = [
                Paragraph(f'<b>{_safe(exp.get("title",""))}</b>  —  {_safe(exp.get("company",""))}', styles["eh"]),
                Paragraph(_safe(exp.get("duration", "")), styles["meta"]),
            ]
            for b in (exp.get("bullets") or []):
                block.append(Paragraph(f"• {_safe(b)}", styles["bullet"]))
            block.append(Spacer(1, 2*mm))
            story.append(KeepTogether(block))

    # Education
    education = resume.get("education") or []
    if education:
        story += _section("Education", styles, theme)
        for edu in education:
            story.append(Paragraph(f'<b>{_safe(edu.get("degree",""))}</b>  —  {_safe(edu.get("institution",""))}', styles["eh"]))
            story.append(Paragraph(_safe(edu.get("year", "")), styles["meta"]))
            story.append(Spacer(1, 2*mm))

    # Projects
    projects = resume.get("projects") or []
    if projects:
        story += _section("Projects", styles, theme)
        for proj in projects:
            tech_str = " · ".join(proj.get("tech") or [])
            block = [Paragraph(f'<b>{_safe(proj.get("name",""))}</b>', styles["eh"]),
                     Paragraph(_safe(proj.get("description", "")), styles["body"])]
            if tech_str:
                block.append(Paragraph(f'<i>{_safe(tech_str)}</i>', styles["meta"]))
            block.append(Spacer(1, 2*mm))
            story.append(KeepTogether(block))

    # Certifications
    certs = resume.get("certifications") or []
    if certs:
        story += _section("Certifications", styles, theme)
        for c in certs:
            story.append(Paragraph(f"• {_safe(c)}", styles["bullet"]))

    doc.build(story)
    return buffer.getvalue()


def generate_cover_letter_pdf(cover_letter: dict) -> bytes:
    theme  = THEMES["Standard Corporate"]
    styles = _build_styles(theme)
    buffer = io.BytesIO()
    doc    = _make_doc(buffer, left=2.5*cm, right=2.5*cm, top=3*cm, bottom=3*cm)
    story: list = []

    if cover_letter.get("applicant_name"):
        story.append(Paragraph(_safe(cover_letter["applicant_name"]), styles["name"]))
    story.append(Paragraph(_safe(cover_letter.get("date", date.today().strftime("%B %d, %Y"))), styles["meta"]))
    story.append(Spacer(1, 8*mm))

    for para in (cover_letter.get("text") or "").split("\n\n"):
        para = para.strip()
        if para:
            story.append(Paragraph(_safe(para), styles["body"]))
            story.append(Spacer(1, 3*mm))

    doc.build(story)
    return buffer.getvalue()
