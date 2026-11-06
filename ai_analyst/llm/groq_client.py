"""
ai_analyst/llm/groq_client.py
Reusable, singleton-style Groq API client with error handling.

Wraps the official `groq` Python SDK (v1.x).
Credentials are read exclusively from settings – never hardcoded.
"""
from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING

from groq import Groq, RateLimitError, APITimeoutError, APIStatusError

from ai_analyst.config import settings

if TYPE_CHECKING:
    from groq.types.chat import ChatCompletion

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Client factory
# ---------------------------------------------------------------------------

_client: Groq | None = None


def get_groq_client() -> Groq:
    """Return (and lazily create) the shared Groq client."""
    global _client
    if _client is None:
        if not settings.groq_configured:
            raise RuntimeError(
                "GROQ_API_KEY is not configured. "
                "Copy .env.example → .env and set your Groq API key."
            )
        _client = Groq(
            api_key=settings.groq_api_key,
            timeout=settings.groq_timeout,
        )
        logger.info("Groq client initialised (model=%s)", settings.groq_model)
    return _client


# ---------------------------------------------------------------------------
# Chat completion helper
# ---------------------------------------------------------------------------

def call_groq(
    system_prompt: str,
    user_prompt: str,
    *,
    temperature: float = 0.0,
    max_tokens: int = 1024,
    retries: int = 2,
) -> str:
    """
    Call the Groq chat-completions endpoint and return the assistant's raw text.

    Parameters
    ----------
    system_prompt : str
        System-level instructions injected as the first message.
    user_prompt : str
        The end-user's natural-language question.
    temperature : float
        Sampling temperature (0 = deterministic).
    max_tokens : int
        Maximum completion tokens.
    retries : int
        Number of automatic retries on rate-limit or timeout errors.

    Returns
    -------
    str
        The raw text content of the first completion choice.

    Raises
    ------
    RuntimeError
        On unrecoverable API errors.
    """
    client = get_groq_client()
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    last_error: Exception | None = None
    for attempt in range(retries + 1):
        try:
            response: ChatCompletion = client.chat.completions.create(
                model=settings.groq_model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                response_format={"type": "json_object"},
            )
            content = response.choices[0].message.content or ""
            logger.debug(
                "Groq response received (attempt=%d, tokens=%s)",
                attempt + 1,
                response.usage,
            )
            return content

        except RateLimitError as exc:
            wait = 2 ** attempt  # 1s, 2s, 4s …
            logger.warning(
                "Groq rate-limit hit (attempt=%d). Retrying in %ds. %s",
                attempt + 1,
                wait,
                exc,
            )
            last_error = exc
            if attempt < retries:
                time.sleep(wait)

        except APITimeoutError as exc:
            logger.warning(
                "Groq API timeout (attempt=%d). Retrying. %s", attempt + 1, exc
            )
            last_error = exc
            if attempt < retries:
                time.sleep(1)

        except APIStatusError as exc:
            logger.error("Groq API status error: %s – %s", exc.status_code, exc)
            raise RuntimeError(
                f"Groq API returned status {exc.status_code}: {exc.message}"
            ) from exc

    raise RuntimeError(
        f"Groq API call failed after {retries + 1} attempts. Last error: {last_error}"
    ) from last_error

