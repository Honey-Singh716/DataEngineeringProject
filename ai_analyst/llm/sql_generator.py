"""
ai_analyst/llm/sql_generator.py
Calls Groq to generate SQL from a natural-language question,
then parses and validates the structured JSON response.

generate_sql(user_question: str) → GeneratedSQL
"""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from typing import Literal, Optional

from ai_analyst.config import settings
from ai_analyst.llm.groq_client import call_groq
from ai_analyst.llm.prompt_templates import SYSTEM_PROMPT, build_user_prompt

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Valid status/chart values – validated on parsing
# ---------------------------------------------------------------------------

_VALID_STATUSES = {"success", "unsupported", "clarification_required"}
_VALID_CHARTS = {"bar", "line", "pie", "scatter", "table", None}
_VALID_CONFIDENCE = {"high", "medium", "low"}

# ---------------------------------------------------------------------------
# Result container
# ---------------------------------------------------------------------------


@dataclass
class GeneratedSQL:
    """
    Structured output from generate_sql().

    Fields
    ------
    status          : 'success' | 'unsupported' | 'clarification_required'
    sql             : Generated SQL string (None if unsupported).
    explanation     : Human-readable explanation.
    chart_type      : Suggested chart for the UI ('bar', 'line', etc.).
    confidence      : LLM confidence ('high', 'medium', 'low').
    raw_response    : Raw JSON string from Groq (useful for debugging).
    parse_errors    : Non-fatal parsing warnings.
    """

    status: Literal["success", "unsupported", "clarification_required"]
    sql: Optional[str]
    explanation: str
    chart_type: Optional[str]
    confidence: str
    raw_response: str = ""
    parse_errors: list[str] = field(default_factory=list)

    @property
    def is_success(self) -> bool:
        return self.status == "success"

    @property
    def is_unsupported(self) -> bool:
        return self.status == "unsupported"

    @property
    def needs_clarification(self) -> bool:
        return self.status == "clarification_required"


# ---------------------------------------------------------------------------
# Main function
# ---------------------------------------------------------------------------


def generate_sql(user_question: str) -> GeneratedSQL:
    """
    Convert a natural-language question into a structured GeneratedSQL object.

    Flow
    ----
    1. Build system + user prompts.
    2. Call Groq API (temperature=0, response_format=json).
    3. Parse JSON response.
    4. Validate response structure.
    5. Return GeneratedSQL.

    SQL is NOT executed here. That is the caller's responsibility.

    Parameters
    ----------
    user_question : str
        The end-user's natural-language question.

    Returns
    -------
    GeneratedSQL
        Always returned; errors surface in parse_errors or status='unsupported'.

    Raises
    ------
    RuntimeError
        If the Groq API call fails (network, auth, rate-limit exhausted).
    """
    if not user_question or not user_question.strip():
        return GeneratedSQL(
            status="clarification_required",
            sql=None,
            explanation="Question is empty. Please provide a road safety question.",
            chart_type=None,
            confidence="low",
        )

    system_prompt = SYSTEM_PROMPT
    user_prompt = build_user_prompt(
        user_question,
        max_rows=settings.max_result_rows,
    )

    logger.info("Sending question to Groq (model=%s): %s", settings.groq_model, user_question[:80])

    # Call Groq (raises RuntimeError on unrecoverable errors)
    raw_response = call_groq(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        temperature=0.0,
        max_tokens=1024,
    )

    return _parse_response(raw_response, user_question)


# ---------------------------------------------------------------------------
# Response parser
# ---------------------------------------------------------------------------


def _parse_response(raw: str, question: str) -> GeneratedSQL:
    """Parse and validate the JSON response from Groq."""
    parse_errors: list[str] = []

    # ── JSON decode ────────────────────────────────────────────────────────
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        logger.error("Groq returned invalid JSON: %s", exc)
        # Attempt to extract JSON from markdown code block
        payload = _extract_json_from_markdown(raw)
        if payload is None:
            return GeneratedSQL(
                status="unsupported",
                sql=None,
                explanation=(
                    "The AI response could not be parsed as JSON. "
                    "Please rephrase your question."
                ),
                chart_type=None,
                confidence="low",
                raw_response=raw,
                parse_errors=[f"JSON decode error: {exc}"],
            )

    if not isinstance(payload, dict):
        return GeneratedSQL(
            status="unsupported",
            sql=None,
            explanation="AI returned an unexpected response format. Please try again.",
            chart_type=None,
            confidence="low",
            raw_response=raw,
            parse_errors=["Response is not a JSON object."],
        )

    # ── Field extraction with defaults ────────────────────────────────────
    status = str(payload.get("status", "unsupported")).lower().strip()
    sql_raw = payload.get("sql")
    explanation = str(payload.get("explanation", "No explanation provided.")).strip()
    chart_type = payload.get("chart_type")
    confidence = str(payload.get("confidence", "medium")).lower().strip()

    # ── Validate status ────────────────────────────────────────────────────
    if status not in _VALID_STATUSES:
        parse_errors.append(
            f"Unknown status '{status}'. Defaulting to 'unsupported'."
        )
        status = "unsupported"

    # ── Validate chart_type ────────────────────────────────────────────────
    if chart_type not in _VALID_CHARTS:
        parse_errors.append(
            f"Unknown chart_type '{chart_type}'. Defaulting to 'table'."
        )
        chart_type = "table"

    # ── Validate confidence ────────────────────────────────────────────────
    if confidence not in _VALID_CONFIDENCE:
        parse_errors.append(
            f"Unknown confidence '{confidence}'. Defaulting to 'medium'."
        )
        confidence = "medium"

    # ── SQL sanity for success status ──────────────────────────────────────
    if status == "success":
        if not sql_raw or not str(sql_raw).strip():
            parse_errors.append("Status is 'success' but 'sql' is empty.")
            status = "unsupported"
            explanation = (
                "The AI indicated success but produced an empty SQL query. "
                "Please rephrase your question."
            )
            sql_raw = None
        else:
            sql_raw = str(sql_raw).strip()
            # Strip markdown code fences if the model added them
            sql_raw = _strip_code_fence(sql_raw)
    else:
        sql_raw = None

    if parse_errors:
        logger.warning("Response parse warnings for question %r: %s", question[:60], parse_errors)

    return GeneratedSQL(
        status=status,
        sql=sql_raw,
        explanation=explanation,
        chart_type=chart_type,
        confidence=confidence,
        raw_response=raw,
        parse_errors=parse_errors,
    )


# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------


def _strip_code_fence(text: str) -> str:
    """Remove ```sql ... ``` or ``` ... ``` markdown wrappers."""
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        # Drop first line (``` or ```sql) and last line (```)
        inner = lines[1:-1] if lines[-1].strip() == "```" else lines[1:]
        return "\n".join(inner).strip()
    return text


def _extract_json_from_markdown(text: str):
    """Try to extract a JSON object from a markdown code block."""
    import re
    patterns = [
        r"```json\s*([\s\S]+?)\s*```",
        r"```\s*([\s\S]+?)\s*```",
        r"(\{[\s\S]+\})",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                continue
    return None

