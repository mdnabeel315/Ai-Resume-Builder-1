"""PDF Service — ReportLab Platypus. 3 themes. Returns bytes."""

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
MH = 1.8 * cm
MV = 1.5 * cm

THEMES = {
    "Standard Corporate": {"accent": colors.HexColor("#1a365d"), "sub": colors.HexColor("#4a5568"), "rule": colors.HexColor("#2b6cb0"), "ns": 22, "hs": 9, "bs": 9, "fn": "Times-Roman",  "fb": "Times-Bold"},
    "Modern Creative":    {"accent": colors.HexColor("#6b21a8"), "sub": colors.HexColor("#553c9a"), "rule": colors.HexColor("#7c3aed"), "ns": 24, "hs": 9, "bs": 9, "fn": "Helvetica",    "fb": "Helvetica-Bold"},
    "Minimal Clean":      {"accent": colors.HexColor("#111827"), "sub": colors.HexColor("#6b7280"), "rule": colors.HexColor("#9ca3af"), "ns": 22, "hs": 8, "bs": 9, "fn": "Helvetica",    "fb": "Helvetica-Bold"},
}


def _x(v: Any) -> str:
    if not v: return ""
    return str(v).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")


def _styles(t):
    fn, fb, acc, sub = t["fn"], t["fb"], t["accent"], t["sub"]
    body = colors.HexColor("#2d2d2d")
    return {
        "name":    ParagraphStyle("nm",  fontName=fb, fontSize=t["ns"], textColor=acc, spaceAfter=1*mm, leading=t["ns"]+2),
        "contact": ParagraphStyle("ct",  fontName=fn, fontSize=7.5, textColor=sub, spaceAfter=3*mm, leading=11),
        "h2":      ParagraphStyle("h2",  fontName=fb, fontSize=t["hs"], textColor=acc, spaceBefore=4*mm, spaceAfter=1*mm, leading=12),
        "eh":      ParagraphStyle("eh",  fontName=fb, fontSize=t["bs"], textColor=colors.HexColor("#1a1a1a"), leading=13),
        "meta":    ParagraphStyle("mt",  fontName=fn, fontSize=8, textColor=sub, leading=11),
        "bullet":  ParagraphStyle("bl",  fontName=fn, fontSize=t["bs"], textColor=body, leftIndent=10, firstLineIndent=-10, leading=12, spaceAfter=1*mm),
        "body":    ParagraphStyle("bd",  fontName=fn, fontSize=t["bs"], textColor=body, leading=13, spaceAfter=2*mm),
    }


def _rule(t): return HRFlowable(width="100%", thickness=0.8, color=t["rule"], spaceAfter=2*mm)
def _sec(title, s, t): return [Paragraph(title.upper(), s["h2"]), _rule(t)]

def _doc(buf, l=MH, r=MH, top=MV, bot=MV):
    doc = BaseDocTemplate(buf, pagesize=A4, leftMargin=l, rightMargin=r, topMargin=top, bottomMargin=bot)
    frame = Frame(l, bot, PAGE_W-l-r, PAGE_H-top-bot, id="main")
    doc.addPageTemplates([PageTemplate(id="main", frames=frame)])
    return doc


def generate_resume_pdf(resume: dict, template_style: str = "Standard Corporate") -> bytes:
    theme = THEMES.get(template_style, THEMES["Standard Corporate"])
    s = _styles(theme)
    buf = io.BytesIO()
    doc = _doc(buf)
    story = []

    contact = resume.get("contact") or {}
    story.append(Paragraph(_x(resume.get("name","Your Name")), s["name"]))
    cp = "  ·  ".join(_x(p) for p in [contact.get("email"), contact.get("phone"), contact.get("linkedin"), contact.get("github")] if p)
    if cp: story.append(Paragraph(cp, s["contact"]))
    story.append(_rule(theme))

    if resume.get("summary"):
        story += _sec("Summary", s, theme)
        story.append(Paragraph(_x(resume["summary"]), s["body"]))

    skills = resume.get("skills") or {}
    tech, soft = skills.get("technical") or [], skills.get("soft") or []
    if tech or soft:
        story += _sec("Skills", s, theme)
        if tech: story.append(Paragraph(f'<b>Technical:</b>  {_x(", ".join(tech))}', s["body"]))
        if soft: story.append(Paragraph(f'<b>Soft Skills:</b>  {_x(", ".join(soft))}', s["body"]))

    exp = resume.get("experience") or []
    if exp:
        story += _sec("Experience", s, theme)
        for e in exp:
            block = [
                Paragraph(f'<b>{_x(e.get("title",""))}</b>  —  {_x(e.get("company",""))}', s["eh"]),
                Paragraph(_x(e.get("duration","")), s["meta"]),
            ]
            for b in (e.get("bullets") or []): block.append(Paragraph(f"• {_x(b)}", s["bullet"]))
            block.append(Spacer(1, 2*mm))
            story.append(KeepTogether(block))

    edu = resume.get("education") or []
    if edu:
        story += _sec("Education", s, theme)
        for e in edu:
            story.append(Paragraph(f'<b>{_x(e.get("degree",""))}</b>  —  {_x(e.get("institution",""))}', s["eh"]))
            story.append(Paragraph(_x(e.get("year","")), s["meta"]))
            story.append(Spacer(1, 2*mm))

    proj = resume.get("projects") or []
    if proj:
        story += _sec("Projects", s, theme)
        for p in proj:
            block = [Paragraph(f'<b>{_x(p.get("name",""))}</b>', s["eh"]),
                     Paragraph(_x(p.get("description","")), s["body"])]
            tech_str = " · ".join(p.get("tech") or [])
            if tech_str: block.append(Paragraph(f'<i>{_x(tech_str)}</i>', s["meta"]))
            block.append(Spacer(1, 2*mm))
            story.append(KeepTogether(block))

    certs = resume.get("certifications") or []
    if certs:
        story += _sec("Certifications", s, theme)
        for c in certs: story.append(Paragraph(f"• {_x(c)}", s["bullet"]))

    doc.build(story)
    return buf.getvalue()


def generate_cover_letter_pdf(cl: dict) -> bytes:
    theme = THEMES["Standard Corporate"]
    s = _styles(theme)
    buf = io.BytesIO()
    doc = _doc(buf, l=2.5*cm, r=2.5*cm, top=3*cm, bot=3*cm)
    story = []

    if cl.get("applicant_name"): story.append(Paragraph(_x(cl["applicant_name"]), s["name"]))
    story.append(Paragraph(_x(cl.get("date", date.today().strftime("%B %d, %Y"))), s["meta"]))
    story.append(Spacer(1, 8*mm))

    for para in (cl.get("text") or "").split("\n\n"):
        para = para.strip()
        if para:
            story.append(Paragraph(_x(para), s["body"]))
            story.append(Spacer(1, 3*mm))

    doc.build(story)
    return buf.getvalue()
