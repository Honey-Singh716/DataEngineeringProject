"""
ai_analyst/database/connection.py
Database connection management for the AI Analyst backend.

Provides two engines:
  - get_readonly_engine()   → read-only role for LLM-generated queries
  - get_admin_engine()      → superuser for schema introspection only (not exposed to LLM)

NEVER mixes read-only execution with the admin/superuser credential.
"""
from __future__ import annotations

import logging
from functools import lru_cache

from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import Engine

from ai_analyst.config import settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Safety defaults injected into every new connection
# ---------------------------------------------------------------------------

_READONLY_INIT_SQL = [
    "SET default_transaction_read_only = on",
    f"SET statement_timeout = '{settings.query_timeout_seconds * 1000}'",
    "SET search_path = road_insight, public",
]


def _apply_readonly_session(dbapi_connection, connection_record):  # noqa: ARG001
    """SQLAlchemy connect event: harden every pooled connection."""
    cursor = dbapi_connection.cursor()
    for sql in _READONLY_INIT_SQL:
        cursor.execute(sql)
    cursor.close()
    dbapi_connection.commit()


# ---------------------------------------------------------------------------
# Public factory – read-only engine
# ---------------------------------------------------------------------------

@lru_cache(maxsize=1)
def get_readonly_engine() -> Engine:
    """
    Return (and lazily create) a SQLAlchemy engine that connects using the
    *dedicated read-only role*.

    Prerequisites
    -------------
    1. Run  scripts/setup_readonly_role.sql  as a PostgreSQL superuser.
    2. Set  READONLY_DATABASE_URL  in .env (see .env.example).

    Raises
    ------
    RuntimeError
        If READONLY_DATABASE_URL has not been configured.
    """
    if not settings.db_configured:
        raise RuntimeError(
            "READONLY_DATABASE_URL is not configured or still contains the "
            "placeholder value 'CHANGE_ME'.\n"
            "→ Run scripts/setup_readonly_role.sql to create the role.\n"
            "→ Then set READONLY_DATABASE_URL in your .env file."
        )

    url = settings.readonly_database_url
    # Mask credentials in log output
    masked = url.split("@")[-1] if "@" in url else url
    logger.info("Creating read-only engine → ...@%s", masked)

    engine = create_engine(
        url,
        pool_pre_ping=True,
        pool_size=3,
        max_overflow=2,
        connect_args={
            "connect_timeout": 5,
            "application_name": "road_insight_ai_analyst",
        },
    )

    # Apply read-only constraints on every new physical connection
    event.listen(engine, "connect", _apply_readonly_session)
    return engine


# ---------------------------------------------------------------------------
# Health-check helper
# ---------------------------------------------------------------------------

def check_readonly_connection() -> dict:
    """
    Attempt to connect using the read-only engine and return a status dict.

    Returns
    -------
    dict  with keys:
        ok        bool
        db_name   str | None
        message   str
    """
    try:
        engine = get_readonly_engine()
        with engine.connect() as conn:
            row = conn.execute(text("SELECT current_database(), current_user")).fetchone()
        return {
            "ok": True,
            "db_name": row[0] if row else None,
            "db_user": row[1] if row else None,
            "message": "Read-only connection established.",
        }
    except RuntimeError as exc:
        return {"ok": False, "db_name": None, "db_user": None, "message": str(exc)}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "db_name": None, "db_user": None, "message": f"Connection failed: {exc}"}

