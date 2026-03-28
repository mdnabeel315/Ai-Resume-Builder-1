"""
LLM Service — Gemini 2.0 Flash with:
  - Tenacity retry (3x, exponential backoff)
  - SHA-256 TTL cache (5 min) to avoid duplicate API calls
  - JSON mode with markdown fence stripping
  - Custom exception hierarchy
"""

import json
import hashlib
import time
import logging
from typing import Any

import google.generativeai as genai
from tenacity import (
    retry, stop_after_attempt, wait_exponential,
    retry_if_exception_type, before_sleep_log,
)

from config import get_settings

logger = logging.getLogger(__name__)

_MODEL_NAME = "gemini-2.0-flash"
_CACHE: dict[str, tuple[Any, float]] = {}
_CACHE_TTL = 300  # seconds


# ── Init ───────────────────────────────────────────────────────────────────────
def _init_genai():
    settings = get_settings()
    genai.configure(api_key=settings.gemini_api_key)

_init_genai()


# ── Cache ──────────────────────────────────────────────────────────────────────
def _cache_key(system: str, user: str) -> str:
    return hashlib.sha256(f"{system}||{user}".encode()).hexdigest()

def _get_cached(key: str) -> Any | None:
    if key in _CACHE:
        val, ts = _CACHE[key]
        if time.time() - ts < _CACHE_TTL:
            return val
        del _CACHE[key]
    return None

def _set_cached(key: str, val: Any) -> None:
    _CACHE[key] = (val, time.time())


# ── Exceptions ─────────────────────────────────────────────────────────────────
class LLMError(Exception):
    """LLM call failed after all retries."""

class LLMParseError(LLMError):
    """LLM returned invalid JSON."""


# ── Raw call with retry ────────────────────────────────────────────────────────
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=8),
    retry=retry_if_exception_type(Exception),
    before_sleep=before_sleep_log(logger, logging.WARNING),
    reraise=True,
)
def _call_gemini(system: str, user: str, temperature: float, max_tokens: int, json_mode: bool) -> str:
    cfg = genai.GenerationConfig(
        temperature=temperature,
        max_output_tokens=max_tokens,
        response_mime_type="application/json" if json_mode else "text/plain",
    )
    model = genai.GenerativeModel(
        model_name=_MODEL_NAME,
        generation_config=cfg,
        system_instruction=system,
    )
    return model.generate_content(user).text.strip()


# ── Public API ─────────────────────────────────────────────────────────────────
def complete(
    system_prompt: str,
    user_prompt: str,
    *,
    temperature: float = 0.7,
    max_tokens: int = 2048,
    json_mode: bool = False,
    use_cache: bool = True,
) -> Any:
    """
    Call Gemini. Returns str (json_mode=False) or dict (json_mode=True).
    Raises LLMError on failure, LLMParseError on bad JSON.
    """
    key = _cache_key(system_prompt, user_prompt)

    if use_cache:
        cached = _get_cached(key)
        if cached is not None:
            logger.debug("LLM cache hit")
            return cached

    try:
        raw = _call_gemini(system_prompt, user_prompt, temperature, max_tokens, json_mode)
    except Exception as e:
        raise LLMError(f"Gemini failed after retries: {e}") from e

    if not json_mode:
        if use_cache:
            _set_cached(key, raw)
        return raw

    # Strip markdown fences
    clean = raw.strip()
    if clean.startswith("```"):
        parts = clean.split("```", 2)
        clean = parts[1]
        if clean.startswith("json"):
            clean = clean[4:]
        clean = clean.rsplit("```", 1)[0].strip()

    try:
        parsed = json.loads(clean)
    except json.JSONDecodeError as e:
        raise LLMParseError(f"JSON parse failed: {e} | Raw: {raw[:300]}") from e

    if use_cache:
        _set_cached(key, parsed)
    return parsed
