"""
ai_analyst/database/query_executor.py
Executes pre-validated SQL against the read-only PostgreSQL engine.

execute_query(sql) → QueryResult
"""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Optional

import pandas as pd
from sqlalchemy import text
from sqlalchemy.exc import OperationalError, ProgrammingError, SQLAlchemyError

from ai_analyst.database.connection import get_readonly_engine
from ai_analyst.config import settings

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Result container
# ---------------------------------------------------------------------------

@dataclass
class QueryResult:
    """Structured return value from execute_query."""
    ok: bool
    data: Optional[pd.DataFrame] = None
    row_count: int = 0
    execution_time_ms: float = 0.0
    error: Optional[str] = None
    is_empty: bool = False

    def to_dict(self) -> dict:
        """Serialisable summary (data as list-of-dicts, not raw DataFrame)."""
        return {
            "ok": self.ok,
            "row_count": self.row_count,
            "execution_time_ms": round(self.execution_time_ms, 1),
            "error": self.error,
            "is_empty": self.is_empty,
            "data": self.data.to_dict(orient="records") if self.data is not None else None,
        }


# ---------------------------------------------------------------------------
# Executor
# ---------------------------------------------------------------------------

def execute_query(validated_sql: str) -> QueryResult:
    """
    Execute a pre-validated SELECT statement on the read-only database role.

    Parameters
    ----------
    validated_sql : str
        A SQL string that has already passed ``sql_validator.validate_sql()``.

    Returns
    -------
    QueryResult
        Always returns a QueryResult; never raises (errors are captured).

    Security contract
    -----------------
    - Uses the *read-only* engine (dedicated role, not postgres superuser).
    - The engine applies ``SET default_transaction_read_only = on`` on connect.
    - The engine applies ``SET statement_timeout = <N>s`` on connect.
    - The transaction is never committed; it is always rolled back after read.
    """
    t0 = time.perf_counter()
    try:
        engine = get_readonly_engine()
    except RuntimeError as exc:
        return QueryResult(ok=False, error=str(exc))

    try:
        with engine.connect() as conn:
            # Wrap in an explicit read-only transaction
            with conn.begin():
                result = conn.execute(text(validated_sql))
                rows = result.fetchmany(settings.max_result_rows + 1)  # +1 to detect overflow
                cols = list(result.keys())

        elapsed_ms = (time.perf_counter() - t0) * 1000

        if not rows:
            logger.info("Query returned 0 rows in %.1f ms.", elapsed_ms)
            return QueryResult(
                ok=True,
                data=pd.DataFrame(columns=cols),
                row_count=0,
                execution_time_ms=elapsed_ms,
                is_empty=True,
            )

        # Warn if result was capped
        if len(rows) > settings.max_result_rows:
            rows = rows[: settings.max_result_rows]
            logger.warning(
                "Query result capped at %d rows (MAX_RESULT_ROWS).",
                settings.max_result_rows,
            )

        df = pd.DataFrame(rows, columns=cols)
        logger.info(
            "Query returned %d rows in %.1f ms.",
            len(df),
            elapsed_ms,
        )
        return QueryResult(
            ok=True,
            data=df,
            row_count=len(df),
            execution_time_ms=elapsed_ms,
            is_empty=False,
        )

    except OperationalError as exc:
        elapsed_ms = (time.perf_counter() - t0) * 1000
        err_str = str(exc.orig) if exc.orig else str(exc)
        if "statement timeout" in err_str.lower() or "canceling statement" in err_str.lower():
            msg = (
                f"Query timed out after {settings.query_timeout_seconds}s. "
                "Try a more specific filter or a simpler query."
            )
        else:
            msg = f"Database connection error: {err_str}"
        logger.error("OperationalError executing query: %s", err_str)
        return QueryResult(ok=False, error=msg, execution_time_ms=elapsed_ms)

    except ProgrammingError as exc:
        elapsed_ms = (time.perf_counter() - t0) * 1000
        err_str = str(exc.orig) if exc.orig else str(exc)
        logger.error("ProgrammingError executing query: %s", err_str)
        return QueryResult(
            ok=False,
            error=f"SQL execution error: {err_str}",
            execution_time_ms=elapsed_ms,
        )

    except SQLAlchemyError as exc:
        elapsed_ms = (time.perf_counter() - t0) * 1000
        logger.error("SQLAlchemy error executing query: %s", exc)
        return QueryResult(
            ok=False,
            error=f"Database error: {exc}",
            execution_time_ms=elapsed_ms,
        )

