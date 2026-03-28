"""
State Manager — single source of truth for all Streamlit session state.
Import from any page: from state_manager import get_resume, set_resume, etc.
"""

import streamlit as st

_KEYS = {
    "zna_parsed":    None,
    "zna_resume":    None,
    "zna_cl":        None,
    "zna_ats":       None,
    "zna_jd":        "",
    "zna_title":     "",
    "zna_history":   [],
}

def _init():
    for k, v in _KEYS.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init()

# ── Resume ─────────────────────────────────────────────────────────────────────
def get_parsed_data():      return st.session_state.get("zna_parsed")
def set_parsed_data(d):     st.session_state["zna_parsed"] = d

def get_resume():           return st.session_state.get("zna_resume")
def set_resume(d):
    st.session_state["zna_resume"] = d
    score = d.get("ats_score", 0) if d else 0
    if isinstance(score, (int, float)) and score > 0:
        h = st.session_state.get("zna_history", [])
        h.append(int(score))
        st.session_state["zna_history"] = h[-10:]

def has_resume():           return st.session_state.get("zna_resume") is not None

# ── Cover Letter ───────────────────────────────────────────────────────────────
def get_cover_letter():     return st.session_state.get("zna_cl")
def set_cover_letter(d):    st.session_state["zna_cl"] = d

# ── ATS ────────────────────────────────────────────────────────────────────────
def get_ats_result():       return st.session_state.get("zna_ats")
def set_ats_result(d):
    st.session_state["zna_ats"] = d
    score = d.get("overall_score", 0) if d else 0
    if isinstance(score, (int, float)):
        h = st.session_state.get("zna_history", [])
        h.append(int(score))
        st.session_state["zna_history"] = h[-10:]

def get_ats_history():      return st.session_state.get("zna_history", [])

# ── Job / Title ────────────────────────────────────────────────────────────────
def get_job_description():  return st.session_state.get("zna_jd", "")
def set_job_description(j): st.session_state["zna_jd"] = j

def get_target_title():     return st.session_state.get("zna_title", "")
def set_target_title(t):    st.session_state["zna_title"] = t

# ── Clear ──────────────────────────────────────────────────────────────────────
def clear_all():
    for k, v in _KEYS.items():
        st.session_state[k] = v
