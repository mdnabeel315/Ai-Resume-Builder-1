import streamlit as st
from backend import generate_cover_letter, generate_cover_letter_pdf, TONES, LLMError
from state_manager import get_resume, has_resume, get_job_description, set_cover_letter, get_cover_letter

st.set_page_config(page_title="Cover Letter", page_icon="✉️", layout="wide")
st.title("✉️ Auto-Cover Letter")
st.caption("Generate a highly personalised cover letter based on your resume.")

if not has_resume():
    st.warning("⚠️ No resume found. Please build your resume in **Smart Resume Builder** first.")
    st.stop()

resume = get_resume()

col1, col2 = st.columns([2, 1])
with col1:
    jd = st.text_area("Target Job Description", value=get_job_description(),
                       placeholder="Paste the job description here…", height=200)
with col2:
    tone = st.selectbox("Letter Tone", TONES)
    st.caption({
        "Professional":  "Formal, confident, achievement-driven.",
        "Enthusiastic":  "Warm, energetic, shows personality.",
        "Concise":       "3 tight paragraphs — no filler.",
    }.get(tone, ""))

if st.button("✨ Generate Cover Letter", type="primary"):
    if not jd.strip():
        st.error("Please paste a Job Description.")
    else:
        with st.spinner("✍️ Crafting your cover letter…"):
            try:
                result = generate_cover_letter(resume, jd, tone)
                set_cover_letter(result)
                st.success(f"✅ Generated! {result['word_count']} words.")
            except LLMError as e:
                st.error(f"AI error: {e}")

cl = get_cover_letter()
if cl:
    st.divider()
    col_prev, col_act = st.columns([3, 1])
    with col_prev:
        edited = st.text_area("📝 Edit if needed:", value=cl.get("text",""), height=380, key="cl_edit")
    with col_act:
        st.metric("Words", cl.get("word_count", 0))
        st.metric("Tone",  cl.get("tone",""))

        try:
            pdf = generate_cover_letter_pdf({**cl, "text": edited})
            st.download_button("⬇️ Download PDF", data=pdf,
                               file_name="cover_letter.pdf", mime="application/pdf")
        except Exception as e:
            st.error(f"PDF error: {e}")

        st.download_button("⬇️ Download .txt", data=edited,
                           file_name="cover_letter.txt", mime="text/plain")
