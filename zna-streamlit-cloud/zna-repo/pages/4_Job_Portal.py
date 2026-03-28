import streamlit as st
from backend import run_ats_scan, LLMError
from backend.llm_service import complete
from state_manager import (get_resume, get_target_title, has_resume,
                            get_job_description, set_job_description)

st.set_page_config(page_title="Job Portal", page_icon="🌐", layout="wide")
st.title("🌐 Job Portal")
st.caption("AI-powered job search strategy tailored to your resume and target role.")

target = get_target_title()

if not target:
    st.warning("💡 Fill out the **Target Job Title** in the Resume Builder to unlock the Job Portal.")
    st.stop()

if has_resume():
    resume = get_resume()
    col_a, col_b = st.columns([3, 1])
    with col_a:
        st.markdown(f"**{resume.get('name','')}** — Target: `{target}`")
    with col_b:
        st.success("Resume Loaded ✅")

if st.button("🤖 Generate Search Strategy", type="primary"):
    skills = (get_resume() or {}).get("skills", {}).get("technical", []) if has_resume() else []
    with st.spinner("🔍 Building your job search strategy…"):
        try:
            system = "You are a job search strategist. Return ONLY valid JSON."
            user = f"""Generate a job search strategy for:
Role: {target}
Skills: {", ".join(skills[:15])}

Return JSON:
{{
  "linkedin_search_url": "https://www.linkedin.com/jobs/search/?keywords=...",
  "recommended_search_terms": [],
  "alternative_job_titles": [],
  "top_companies_to_target": [{{"name":"","reason":""}}],
  "salary_range": {{"india_lpa":"","us_usd":"","uk_gbp":""}},
  "search_tips": [],
  "certifications_to_boost_profile": []
}}"""
            data = complete(system, user, temperature=0.3, max_tokens=1500, json_mode=True)
            st.session_state["zna_strategy"] = data
        except LLMError as e:
            st.error(f"Strategy failed: {e}")

strategy = st.session_state.get("zna_strategy")
if strategy:
    st.divider()

    url = strategy.get("linkedin_search_url","")
    if url:
        st.subheader("🔗 LinkedIn Job Search")
        st.markdown(f'<a href="{url}" target="_blank" style="background:#0077b5;color:white;padding:8px 18px;border-radius:6px;text-decoration:none;font-weight:600">🔍 Open LinkedIn Jobs →</a>', unsafe_allow_html=True)
        st.caption(url)
        st.markdown("")

    col1, col2 = st.columns(2)
    with col1:
        alts = strategy.get("alternative_job_titles",[])
        if alts:
            st.subheader("📋 Alternative Titles")
            st.markdown(" ".join(f"`{t}`" for t in alts))

        terms = strategy.get("recommended_search_terms",[])
        if terms:
            st.subheader("🔎 Search Terms")
            st.markdown(" ".join(f"`{t}`" for t in terms))

        salary = strategy.get("salary_range",{})
        if any(salary.values()):
            st.subheader("💰 Salary Range")
            sc1, sc2, sc3 = st.columns(3)
            with sc1: st.metric("India", salary.get("india_lpa","N/A"))
            with sc2: st.metric("USA",   salary.get("us_usd","N/A"))
            with sc3: st.metric("UK",    salary.get("uk_gbp","N/A"))

    with col2:
        companies = strategy.get("top_companies_to_target",[])
        if companies:
            st.subheader("🏢 Top Companies")
            for co in companies:
                with st.expander(f"🏢 {co.get('name','')}"):
                    st.write(co.get("reason",""))

        tips = strategy.get("search_tips",[])
        if tips:
            st.subheader("💡 Search Tips")
            for tip in tips: st.markdown(f"- {tip}")

        certs = strategy.get("certifications_to_boost_profile",[])
        if certs:
            st.subheader("🏅 Certifications")
            st.markdown(" ".join(f"`{c}`" for c in certs))

st.divider()
st.subheader("⚡ Quick ATS Check")
jd = st.text_area("Paste any job posting to instantly score your resume:",
                   value=get_job_description(), height=120, key="portal_jd")

if st.button("🚀 Quick Scan"):
    if not has_resume():
        st.warning("Build your resume first.")
    elif not jd.strip():
        st.error("Paste a job description.")
    else:
        set_job_description(jd)
        with st.spinner("Scanning…"):
            try:
                result = run_ats_scan(get_resume(), jd)
                score  = result.get("overall_score", 0)
                verdict= result.get("verdict","")
                missing= result.get("missing_keywords",[])
                matched= result.get("matched_keywords",[])

                col_sc, col_vd = st.columns([1, 2])
                with col_sc:
                    st.metric("ATS Score", f"{score}%")
                    st.progress(score / 100)
                with col_vd:
                    st.markdown(f"### {verdict}")
                    if missing:
                        st.markdown("**Add these keywords:**")
                        st.markdown(" ".join(f"`{k}`" for k in missing[:12]))
                if matched:
                    st.markdown("**Already matched:**")
                    st.markdown(" ".join(f"`{k}`" for k in matched[:12]))
            except LLMError as e:
                st.error(f"Scan failed: {e}")
