"""
Global error handling for production resilience.
Streamlit context-aware error display + structured logging.
"""

import time
import traceback
import functools
from typing import Callable, Any

import streamlit as st
import structlog

logger = structlog.get_logger(__name__)


class BackendErrorHandler:
    """Central error interceptor for all backend services."""

    def __init__(self, max_errors_per_minute: int = 5):
        self.error_count = 0
        self.max_errors_per_minute = max_errors_per_minute
        self._window_start = time.time()

    def _reset_window_if_needed(self) -> None:
        """Reset error count every 60 seconds."""
        if time.time() - self._window_start > 60:
            self.error_count = 0
            self._window_start = time.time()

    def intercept(self, func: Callable) -> Callable:
        """Decorator: wrap service calls with error handling and Streamlit feedback."""

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                self._reset_window_if_needed()
                self.error_count += 1
                error_id = f"ERR-{int(time.time())}-{self.error_count}"

                logger.error(
                    "Backend service failed",
                    func=func.__name__,
                    error=str(e),
                    error_id=error_id,
                    traceback=traceback.format_exc(),
                )

                # Circuit breaker gate — stop the app if hammering
                if self.error_count >= self.max_errors_per_minute:
                    st.error(
                        "🚧 Service temporarily unavailable — too many errors. "
                        "Please wait 60 seconds and retry."
                    )
                    st.stop()

                # User-friendly message
                st.error(
                    f"⚠️ Backend error (ID: **{error_id}**). "
                    "Please try again or refresh the page."
                )
                logger.warning("Operation failed — user notified", error_id=error_id)
                return None

        return wrapper

    def safe_llm_call(self, llm_func: Callable, *args, **kwargs) -> Any:
        """Specialised LLM call wrapper with a static fallback response."""
        try:
            return llm_func(*args, **kwargs)
        except Exception as e:
            logger.error("LLM call failed — returning fallback", error=str(e))
            return self._llm_fallback()

    def _llm_fallback(self) -> dict:
        """Static fallback response for total LLM failures."""
        return {
            "name": "Fallback Resume",
            "summary": "Resume generation temporarily unavailable. Please try again shortly.",
            "skills": {"technical": [], "soft": []},
            "experience": [],
            "education": [],
            "ats_score": 0,
            "template_style": "Standard Corporate",
        }


# Global singleton
error_handler = BackendErrorHandler()
