"""
ai_analyst/services/text_to_sql_service.py
Main orchestration service for the full Text-to-SQL pipeline.

Public API:
    run_text_to_sql(user_question: str) → TextToSQLResponse
"""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Literal, Optional

import pandas as pd

from ai_analyst.config import settings
from ai_analyst.database.connection import check_readonly_connection
from ai_analyst.database.query_executor import execute_query, QueryResult
from ai_analyst.llm.sql_generator import generate_sql, GeneratedSQL
from ai_analyst.security.sql_validator import validate_sql, ValidationResult

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Response container
# ---------------------------------------------------------------------------


@dataclass
class TextToSQLResponse:
    """
    Structured response from the full Text-to-SQL pipeline.

    Fields
    ------
    status          : Pipeline outcome status.
    question        : Original user question.
    sql             : Final (validated) SQL that was executed (or None).
    explanation     : AI-generated explanation.
    data            : Pandas DataFrame with results (or None).
    row_count       : Number of rows returned.
    execution_time_ms: DB query execution time in milliseconds.
    chart_type      : Suggested chart type for the UI.
    confidence      : LLM confidence level.
    error           : Human-readable error message (or None).
    validation_warnings: Non-fatal warnings from the SQL validator.
    total_time_ms   : Total end-to-end latency including LLM call.
    """

    status: Literal[
        "success",
        "unsupported",
        "clarification_required",
        "validation_error",
        "execution_error",
        "db_not_configured",
        "llm_error",
        "empty_result",
        "invalid_input",
    ]
    question: str
    sql: Optional[str] = None
    explanation: str = ""
    data: Optional[pd.DataFrame] = None
    row_count: int = 0
    execution_time_ms: float = 0.0
    chart_type: Optional[str] = None
    confidence: str = "low"
    error: Optional[str] = None
    validation_warnings: list[str] = field(default_factory=list)
    total_time_ms: float = 0.0

    def to_dict(self) -> dict:
        """Serialisable summary (data as list-of-dicts)."""
        return {
            "status": self.status,
            "question": self.question,
            "sql": self.sql,
            "explanation": self.explanation,
            "data": self.data.to_dict(orient="records") if self.data is not None else None,
            "row_count": self.row_count,
            "execution_time_ms": round(self.execution_time_ms, 1),
            "chart_type": self.chart_type,
            "confidence": self.confidence,
            "error": self.error,
            "validation_warnings": self.validation_warnings,
            "total_time_ms": round(self.total_time_ms, 1),
        }


# ---------------------------------------------------------------------------
# Main service function
# ---------------------------------------------------------------------------


def run_text_to_sql(user_question: str) -> TextToSQLResponse:
    """
    Execute the full Text-to-SQL pipeline for a single natural-language question.

    Pipeline steps
    --------------
    1.  Validate user input (empty-check, length guard).
    2.  Generate SQL via Groq (prompt → JSON response).
    3.  Parse structured LLM response.
    4.  Handle unsupported questions gracefully.
    5.  Handle clarification requests gracefully.
    6.  Validate generated SQL (AST-based, multi-layer security).
    7.  Verify read-only DB connection is configured.
    8.  Execute validated SQL using the read-only engine.
    9.  Return structured TextToSQLResponse with DataFrame.

    Parameters
    ----------
    user_question : str
        Raw natural-language question from the user.

    Returns
    -------
    TextToSQLResponse
        Always returned; never raises.
    """
    t_start = time.perf_counter()

    # ── Step 1: Validate user input ────────────────────────────────────────
    if not user_question or not user_question.strip():
        return TextToSQLResponse(
            status="invalid_input",
            question=user_question or "",
            error="Please enter a question.",
            total_time_ms=0.0,
        )

    question = user_question.strip()

    # Basic length guard
    if len(question) > 500:
        return TextToSQLResponse(
            status="invalid_input",
            question=question,
            error=(
                f"Question is too long ({len(question)} characters). "
                "Please keep questions under 500 characters."
            ),
            total_time_ms=0.0,
        )

    logger.info("Pipeline started for question: %s", question[:80])

    # ── Step 2 & 3: Generate SQL from Groq ────────────────────────────────
    try:
        generated: GeneratedSQL = generate_sql(question)
    except RuntimeError as exc:
        elapsed = (time.perf_counter() - t_start) * 1000
        logger.error("Groq call failed: %s", exc)
        return TextToSQLResponse(
            status="llm_error",
            question=question,
            error=f"AI service error: {exc}",
            total_time_ms=elapsed,
        )

    # ── Step 4: Handle unsupported questions ──────────────────────────────
    if generated.is_unsupported:
        elapsed = (time.perf_counter() - t_start) * 1000
        return TextToSQLResponse(
            status="unsupported",
            question=question,
            explanation=generated.explanation,
            chart_type=generated.chart_type,
            confidence=generated.confidence,
            error=generated.explanation,
            total_time_ms=elapsed,
        )

    # ── Step 5: Handle clarification requests ─────────────────────────────
    if generated.needs_clarification:
        elapsed = (time.perf_counter() - t_start) * 1000
        return TextToSQLResponse(
            status="clarification_required",
            question=question,
            explanation=generated.explanation,
            chart_type=generated.chart_type,
            confidence=generated.confidence,
            error=generated.explanation,
            total_time_ms=elapsed,
        )

    # ── Step 6: Validate generated SQL ────────────────────────────────────
    validation: ValidationResult = validate_sql(
        generated.sql,
        max_rows=settings.max_result_rows,
    )

    if not validation.ok:
        elapsed = (time.perf_counter() - t_start) * 1000
        logger.warning("SQL validation failed: %s", validation.error_message)
        return TextToSQLResponse(
            status="validation_error",
            question=question,
            sql=generated.sql,
            explanation=generated.explanation,
            chart_type=generated.chart_type,
            confidence=generated.confidence,
            error=f"SQL failed security validation: {validation.error_message}",
            total_time_ms=elapsed,
        )

    validated_sql = validation.sql

    # ── Step 7: Check DB connection is configured ─────────────────────────
    if not settings.db_configured:
        elapsed = (time.perf_counter() - t_start) * 1000
        return TextToSQLResponse(
            status="db_not_configured",
            question=question,
            sql=validated_sql,
            explanation=generated.explanation,
            chart_type=generated.chart_type,
            confidence=generated.confidence,
            validation_warnings=validation.warnings,
            error=(
                "⚠️ Read-only database role is not configured.\n"
                "SQL was generated and validated successfully, but cannot be executed.\n"
                "→ Run scripts/setup_readonly_role.sql as a PostgreSQL administrator.\n"
                "→ Set READONLY_DATABASE_URL in your .env file."
            ),
            total_time_ms=elapsed,
        )

    # ── Step 8: Execute SQL ────────────────────────────────────────────────
    result: QueryResult = execute_query(validated_sql)
    total_elapsed = (time.perf_counter() - t_start) * 1000

    if not result.ok:
        return TextToSQLResponse(
            status="execution_error",
            question=question,
            sql=validated_sql,
            explanation=generated.explanation,
            chart_type=generated.chart_type,
            confidence=generated.confidence,
            validation_warnings=validation.warnings,
            error=result.error,
            total_time_ms=total_elapsed,
        )

    if result.is_empty:
        return TextToSQLResponse(
            status="empty_result",
            question=question,
            sql=validated_sql,
            explanation=generated.explanation,
            data=result.data,
            row_count=0,
            execution_time_ms=result.execution_time_ms,
            chart_type=generated.chart_type,
            confidence=generated.confidence,
            validation_warnings=validation.warnings,
            error=None,
            total_time_ms=total_elapsed,
        )

    # ── Step 9: Return success ─────────────────────────────────────────────
    return TextToSQLResponse(
        status="success",
        question=question,
        sql=validated_sql,
        explanation=generated.explanation,
        data=result.data,
        row_count=result.row_count,
        execution_time_ms=result.execution_time_ms,
        chart_type=generated.chart_type,
        confidence=generated.confidence,
        validation_warnings=validation.warnings,
        total_time_ms=total_elapsed,
    )

