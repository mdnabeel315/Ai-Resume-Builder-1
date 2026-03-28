import streamlit as st
from backend import run_ats_scan, score_label, LLMError
from state_manager import get_resume, has_resume, get_job_description, set_job_description, set_ats_result, get_ats_result

st.set_page_config(page_title="ATS Engine", page_icon="🔍", layout="wide")
st.title("🔍 ATS Match Engine")
st.caption("Compare your resume against a real Job Description to find missing keywords before you apply.")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Your Active Resume")
    if has_resume():
        resume = get_resume()
        st.success(f"✅ Loaded: **{resume.get('name','')}**")
        tech = (resume.get("skills") or {}).get("technical", [])
        if tech: st.caption("Skills: " + ", ".join(tech[:8]))
    else:
        st.warning("⚠️ No resume loaded. Go to **Smart Resume Builder** first.")

with col2:
    st.subheader("Target Job Description")
    jd = st.text_area("Paste the full Job Description:",
                       value=get_job_description(),
                       placeholder="Paste the job requirements, skills, and responsibilities…",
                       height=180)
    if jd != get_job_description():
        set_job_description(jd)

if st.button("🚀 Run Deep ATS Scan", type="primary"):
    if not has_resume():
        st.error("Build your resume first.")
    elif not jd.strip():
        st.error("Please paste a Job Description.")
    else:
        with st.spinner("🔍 Running semantic ATS analysis…"):
            try:
                result = run_ats_scan(get_resume(), jd)
                set_ats_result(result)
            except LLMError as e:
                st.error(f"Scan failed: {e}")

result = get_ats_result()
if result:
    st.divider()
    overall = result.get("overall_score", 0)

    col_s, col_v = st.columns([1, 2])
    with col_s:
        st.metric("Overall ATS Score", f"{overall}%")
        st.progress(overall / 100)
    with col_v:
        st.markdown(f"### {score_label(overall)}")

    st.subheader("📊 Score Breakdown")
    bd = result.get("breakdown", {})
    c1, c2, c3, c4 = st.columns(4)
    for col, (k, label) in zip([c1,c2,c3,c4], [
        ("keyword_match","Keyword Match"),
        ("skills_alignment","Skills Alignment"),
        ("experience_relevance","Experience"),
        ("title_match","Title Match"),
    ]):
        with col:
            st.metric(label, f"{bd.get(k,0)}%")
            st.progress(bd.get(k,0) / 100)

    col_m, col_ms = st.columns(2)
    with col_m:
        st.subheader("✅ Matched Keywords")
        matched = result.get("matched_keywords", [])
        if matched: st.markdown(" ".join(f"`{k}`" for k in matched))
        else: st.caption("None found.")

    with col_ms:
        st.subheader("❌ Missing Keywords")
        missing = result.get("missing_keywords", [])
        if missing: st.markdown(" ".join(f"`{k}`" for k in missing))
        else: st.caption("Great coverage — none missing!")

    improvements = result.get("improvements", [])
    if improvements:
        st.subheader("💡 Improvement Suggestions")
        for imp in improvements:
            with st.expander(f"📌 {imp.get('section','')}"):
                st.markdown(f"**Issue:** {imp.get('issue','')}")
                st.markdown(f"**Fix:** {imp.get('suggestion','')}")

    strengths = result.get("strengths", [])
    if strengths:
        st.subheader("💪 Strengths")
        for s in strengths:
            st.markdown(f"- {s}")
