"""
ZNA AI Studio — Main Dashboard
Run with: streamlit run app.py
"""

import os

import pandas as pd
import streamlit as st

# ── Page config (must be first Streamlit call) ─────────────────────────────────
st.set_page_config(
    page_title="ZNA AI Studio",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Logo path helper ───────────────────────────────────────────────────────────
_LOGO_PATH = os.path.join(os.path.dirname(__file__), "assets", "zna_logo.png")


def _show_logo(width: int = 180) -> None:
    """Display the ZNA logo if the asset exists; fall back to styled text."""
    if os.path.exists(_LOGO_PATH):
        st.image(_LOGO_PATH, width=width)
    else:
        st.markdown(
            """
            <p style="
                font-family:'Syne',sans-serif;
                font-size:32px;font-weight:900;
                background:linear-gradient(135deg,#3b8bff,#7b5cf0,#00d68f);
                -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                background-clip:text;letter-spacing:-0.04em;margin:0;
            ">ZNA✦</p>
            """,
            unsafe_allow_html=True,
        )


# ── Global CSS ─────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    /* Tighten sidebar nav spacing */
    [data-testid="stSidebarNav"] { padding-top: 0.25rem; }
    [data-testid="stSidebarNav"] li { margin-bottom: 2px; }
    /* Metric label + value sizing */
    .stMetric label                              { font-size: 12px !important; }
    .stMetric [data-testid="stMetricValue"]      { font-size: 22px !important; }
    /* Sidebar logo area */
    [data-testid="stSidebar"] .sidebar-logo-wrap { margin-bottom: 12px; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    # Company logo at the top of every page's sidebar
    _show_logo(width=160)
    st.caption("**AI Resume Builder** · Innovate Your Career")
    st.markdown("---")

    from state_manager import get_target_title, get_resume, has_resume

    target = get_target_title()
    if target:
        st.success(f"🎯 **{target}**")
    else:
        st.info("💡 Fill in **Target Job Title** in Resume Builder to unlock the Job Portal.")

    if has_resume():
        r = get_resume()
        st.caption(f"📄 Resume loaded: **{r.get('name', 'User')}**")

    st.markdown("---")
    # Quick link back to the landing page
    st.markdown(
        "[← Back to Landing Page](http://localhost:5500/index.html)",
        help="Open the HTML landing page",
    )

# ── Dashboard header ───────────────────────────────────────────────────────────
col_title, col_logo = st.columns([4, 1])
with col_title:
    st.title("Welcome to your Career Workspace 🔗")
    st.caption("Your central hub for AI-powered career growth and optimisation.")
with col_logo:
    _show_logo(width=120)

# ── Top metrics ────────────────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Dynamic Templates", "3 Styles", delta="Active ●")
with col2:
    st.metric("Input Modes", "Dual", delta="Enabled ⚡")
with col3:
    st.metric("Cover Letters", "Auto-Gen", delta="Ready 📋")
with col4:
    st.metric("ATS Scanner", "Semantic NLP", delta="Online 🚀")

st.divider()

# ── ATS Trend chart + Live system logs ────────────────────────────────────────
from state_manager import get_ats_history

col_chart, col_logs = st.columns([1.5, 1])

with col_chart:
    st.subheader("📈 ATS Optimisation Trends")
    history = get_ats_history()
    chart_data = history if history else [65, 70, 68, 75, 82, 85, 92]
    df = pd.DataFrame(
        {
            "Session": list(range(1, len(chart_data) + 1)),
            "ATS Match Score (%)": chart_data,
        }
    )
    st.line_chart(df.set_index("Session"))
    if not history:
        st.caption("_Sample data shown — generate your first resume to start tracking._")

with col_logs:
    st.subheader("⚡ Live System Logs")

    # Check API key
    gemini_key = ""
    try:
        gemini_key = st.secrets.get("GEMINI_API_KEY", "")
    except Exception:
        gemini_key = os.environ.get("GEMINI_API_KEY", "")

    if gemini_key:
        st.success("✅ **[API]** Gemini 2.0 Flash connected.")
    else:
        st.error(
            "❌ **[API]** `GEMINI_API_KEY` not set.  \n"
            "Add it to `.streamlit/secrets.toml` or set it as an env var."
        )

    st.info("ℹ️ **[Module]** PDF generation engine ready.")

    from state_manager import get_resume, has_resume

    if has_resume():
        resume = get_resume()
        st.warning(
            f"⏳ **[Memory]** Resume loaded for **{resume.get('name', 'user')}**."
        )
    else:
        st.warning("⏳ **[Memory]** Waiting for user to generate a resume...")

st.divider()

# ── Quick-start cards ──────────────────────────────────────────────────────────
st.subheader("🚀 Quick Start")
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(
        "**📄 Resume Builder**  \n"
        "Parse LinkedIn/resume text and generate a polished, ATS-optimised resume."
    )
with c2:
    st.markdown(
        "**✉️ Cover Letter**  \n"
        "Auto-generate a tailored cover letter from your resume + job description."
    )
with c3:
    st.markdown(
        "**🔍 ATS Engine**  \n"
        "Deep scan: compare your resume to any job description with keyword breakdown."
    )
with c4:
    st.markdown(
        "**🌐 Job Portal**  \n"
        "Get AI-powered LinkedIn search strategy, company targets, and salary ranges."
    )
