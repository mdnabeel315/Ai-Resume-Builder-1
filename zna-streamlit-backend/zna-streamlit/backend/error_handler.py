"""
Error Handler — Production resilience layer for all backend services.

Provides:
  - @error_handler.intercept decorator: wraps any service function with
    structured logging + Streamlit UI error feedback
  - safe_llm_call: specialised wrapper with a static fallback resume
  - Circuit breaker: halts the app if too many errors occur in a window
  - Human-readable error IDs for user support
"""

from __future__ import annotations

import functools
import logging
import time
import traceback
from typing import Any, Callable

import streamlit as st

logger = logging.getLogger(__name__)


class BackendErrorHandler:
    """Central error interceptor for all ZNA backend services."""

    def __init__(self, max_errors_per_minute: int = 5):
        self._max_errors = max_errors_per_minute
        self._error_count = 0
        self._window_start = time.time()

    # ── Private helpers ────────────────────────────────────────────────────────
    def _reset_window_if_needed(self) -> None:
        if time.time() - self._window_start > 60:
            self._error_count = 0
            self._window_start = time.time()

    def _make_error_id(self) -> str:
        return f"ERR-{int(time.time())}-{self._error_count:03d}"

    # ── Decorator ──────────────────────────────────────────────────────────────
    def intercept(self, func: Callable) -> Callable:
        """
        Decorator — wrap a service function with structured error handling.

        On success  → returns the function result unchanged.
        On failure  → logs the error, shows Streamlit UI feedback, returns None.
                      If the error rate exceeds the limit, stops the app.
        """

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)

            except Exception as exc:
                self._reset_window_if_needed()
                self._error_count += 1
                error_id = self._make_error_id()

                logger.error(
                    "Backend service failed | func=%s | id=%s | error=%s\n%s",
                    func.__name__,
                    error_id,
                    str(exc),
                    traceback.format_exc(),
                )

                # Circuit-breaker: too many errors in one minute
                if self._error_count >= self._max_errors:
                    st.error(
                        "🚧 **Service temporarily unavailable** — too many errors detected. "
                        "Please wait 60 seconds and try again."
                    )
                    logger.critical(
                        "Circuit breaker tripped — halting app. errors=%d",
                        self._error_count,
                    )
                    st.stop()

                # User-friendly feedback
                st.error(
                    f"⚠️ **Something went wrong** (ID: `{error_id}`).  \n"
                    "Please try again or refresh the page. "
                    "If this persists, check your Gemini API key."
                )
                return None

        return wrapper

    # ── LLM-specific helper ────────────────────────────────────────────────────
    def safe_llm_call(self, llm_func: Callable, *args, **kwargs) -> Any:
        """
        Call an LLM function and fall back to a safe default resume dict if it
        raises any exception. Does NOT trigger the circuit breaker.
        """
        try:
            return llm_func(*args, **kwargs)
        except Exception as exc:
            logger.error("LLM call failed — returning fallback resume: %s", exc)
            return self._llm_fallback()

    # ── Static fallback ────────────────────────────────────────────────────────
    @staticmethod
    def _llm_fallback() -> dict:
        """Minimal safe resume dict used when the LLM is completely unavailable."""
        return {
            "name": "Fallback Resume",
            "contact": {"email": "", "phone": "", "github": "", "linkedin": ""},
            "summary": (
                "Resume generation is temporarily unavailable. "
                "Please try again shortly."
            ),
            "skills": {"technical": [], "soft": []},
            "experience": [],
            "education": [],
            "projects": [],
            "certifications": [],
            "ats_score": 0,
            "template_style": "Standard Corporate",
        }


# ── Module-level singleton ─────────────────────────────────────────────────────
error_handler = BackendErrorHandler()
