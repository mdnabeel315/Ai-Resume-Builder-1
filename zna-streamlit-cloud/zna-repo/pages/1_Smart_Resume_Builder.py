import streamlit as st
from backend import parse_and_generate, generate_resume_pdf, TEMPLATE_STYLES, LLMError
from state_manager import set_resume, set_parsed_data, set_target_title, get_target_title

st.set_page_config(page_title="Resume Builder", page_icon="📄", layout="wide")
st.title("📄 Smart Resume Builder")

# ── Template ──────────────────────────────────────────────────────────────────
st.subheader("⚙️ Template Settings")
template = st.selectbox("Select Professional Template Style:", TEMPLATE_STYLES)
st.divider()

# ── Input mode ────────────────────────────────────────────────────────────────
st.subheader("📋 Data Input")
mode = st.radio("Input method:", ["⚡ Auto-Parse (Paste LinkedIn / Resume Text)", "✍️ Manual Entry"],
                horizontal=True)

if mode.startswith("⚡"):
    st.info("💡 Paste your entire LinkedIn profile or old resume — the AI extracts everything automatically.")

col1, col2 = st.columns(2)
with col1:
    name  = st.text_input("Full Name",           placeholder="e.g. Syed Zaid Karim")
    email = st.text_input("Email")
    github= st.text_input("GitHub URL")
with col2:
    target = st.text_input("Target Job Title *",  placeholder="e.g. Software Engineer",
                            value=get_target_title())
    phone  = st.text_input("Phone Number")
    linkedin_url = st.text_input("LinkedIn URL")

raw_text = st.text_area(
    "Raw Experience / Education / LinkedIn Data *",
    placeholder="Paste your resume or LinkedIn profile text here…",
    height=180,
)

error_placeholder = st.empty()

if st.button("✨ Auto Generate AI Resume", type="primary"):
    if not raw_text.strip():
        error_placeholder.error("Please paste your background text.")
    elif not target.strip():
        error_placeholder.error("Please enter a Target Job Title.")
    else:
        set_target_title(target.strip())
        with st.spinner("🤖 AI is generating your resume…"):
            try:
                overrides = {k: v for k, v in {"name": name, "email": email,
                             "phone": phone, "github": github, "linkedin": linkedin_url}.items() if v.strip()}
                parsed, resume = parse_and_generate(raw_text, target, template, overrides=overrides)
                set_parsed_data(parsed)
                set_resume(resume)
                st.success(f"✅ Resume generated! ATS Score: **{resume.get('ats_score', 'N/A')}%**")
            except LLMError as e:
                st.error(f"AI error: {e}")
            except Exception as e:
                st.error(f"Error: {e}")

# ── Output ────────────────────────────────────────────────────────────────────
from state_manager import get_resume
resume = get_resume()

if resume:
    st.divider()
    st.subheader("2. AI Output & Export")

    tab1, tab2 = st.tabs(["📋 Resume Preview", "📥 Download PDF"])

    with tab1:
        col_a, col_b = st.columns([3, 1])
        with col_a:
            st.markdown(f"### {resume.get('name','')}")
            contact = resume.get("contact", {})
            parts = [contact.get("email"), contact.get("phone"),
                     contact.get("linkedin"), contact.get("github")]
            st.caption("  ·  ".join(p for p in parts if p))

            if resume.get("summary"):
                st.markdown("**Summary**")
                st.write(resume["summary"])

            skills = resume.get("skills", {})
            if skills.get("technical"):
                st.markdown(f"**Technical:** {', '.join(skills['technical'])}")
            if skills.get("soft"):
                st.markdown(f"**Soft Skills:** {', '.join(skills['soft'])}")

            for exp in resume.get("experience", []):
                st.markdown(f"**{exp.get('title')}** — {exp.get('company')} _{exp.get('duration')}_")
                for b in exp.get("bullets", []):
                    st.markdown(f"- {b}")

            for edu in resume.get("education", []):
                st.markdown(f"**{edu.get('degree')}** — {edu.get('institution')} _{edu.get('year')}_")

        with col_b:
            st.metric("ATS Score", f"{resume.get('ats_score', 0)}%")
            st.metric("Template",  resume.get("template_style", template))

    with tab2:
        with st.spinner("Generating PDF…"):
            try:
                pdf_bytes = generate_resume_pdf(resume, template)
                fname = f"{(resume.get('name') or 'resume').replace(' ','_')}_resume.pdf"
                st.download_button("⬇️ Download Resume PDF", data=pdf_bytes,
                                   file_name=fname, mime="application/pdf")
            except Exception as e:
                st.error(f"PDF error: {e}")
