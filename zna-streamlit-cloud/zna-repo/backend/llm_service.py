"""
LLM Service — Gemini 2.0 Flash with retry + TTL cache.
Reads API key from st.secrets first, then env var.
"""

import json, hashlib, time, logging, os
from typing import Any
import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

logger = logging.getLogger(__name__)
_MODEL  = "gemini-2.0-flash"
_CACHE: dict[str, tuple[Any, float]] = {}
_TTL    = 300


def _api_key() -> str:
    try:
        import streamlit as st
        key = st.secrets.get("GEMINI_API_KEY", "")
        if key:
            return key
    except Exception:
        pass
    key = os.environ.get("GEMINI_API_KEY", "")
    if not key:
        raise EnvironmentError("GEMINI_API_KEY not found in Streamlit Secrets or environment.")
    return key


genai.configure(api_key=_api_key())


class LLMError(Exception):
    pass

class LLMParseError(LLMError):
    pass


def _cache_key(s, u):
    return hashlib.sha256(f"{s}||{u}".encode()).hexdigest()

def _cached(k):
    if k in _CACHE:
        v, ts = _CACHE[k]
        if time.time() - ts < _TTL:
            return v
        del _CACHE[k]
    return None

def _store(k, v):
    _CACHE[k] = (v, time.time())


@retry(stop=stop_after_attempt(3),
       wait=wait_exponential(multiplier=1, min=2, max=8),
       retry=retry_if_exception_type(Exception),
       reraise=True)
def _call(system, user, temperature, max_tokens, json_mode):
    cfg = genai.GenerationConfig(
        temperature=temperature,
        max_output_tokens=max_tokens,
        response_mime_type="application/json" if json_mode else "text/plain",
    )
    model = genai.GenerativeModel(
        model_name=_MODEL,
        generation_config=cfg,
        system_instruction=system,
    )
    return model.generate_content(user).text.strip()


def complete(system_prompt, user_prompt, *, temperature=0.7,
             max_tokens=2048, json_mode=False, use_cache=True):
    key = _cache_key(system_prompt, user_prompt)
    if use_cache:
        hit = _cached(key)
        if hit is not None:
            return hit

    try:
        raw = _call(system_prompt, user_prompt, temperature, max_tokens, json_mode)
    except Exception as e:
        raise LLMError(f"Gemini failed: {e}") from e

    if not json_mode:
        if use_cache: _store(key, raw)
        return raw

    clean = raw.strip()
    if clean.startswith("```"):
        clean = clean.split("```", 2)[1]
        if clean.startswith("json"): clean = clean[4:]
        clean = clean.rsplit("```", 1)[0].strip()

    try:
        parsed = json.loads(clean)
    except json.JSONDecodeError as e:
        raise LLMParseError(f"JSON parse failed: {e} | Raw: {raw[:200]}") from e

    if use_cache: _store(key, parsed)
    return parsed
