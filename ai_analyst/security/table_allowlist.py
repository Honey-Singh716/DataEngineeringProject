"""
ai_analyst/security/table_allowlist.py
Canonical allowed tables and forbidden patterns used by the SQL validator.

Centralised here so both the validator and schema context stay in sync.
"""
from __future__ import annotations

from ai_analyst.database.schema_context import ALLOWED_TABLES, ALLOWED_SCHEMA

# Re-export so other modules can import from one place
__all__ = ["ALLOWED_TABLES", "ALLOWED_SCHEMA", "FORBIDDEN_SCHEMAS", "FORBIDDEN_TABLE_PATTERNS"]

# Schemas that must never appear in generated SQL
FORBIDDEN_SCHEMAS: frozenset[str] = frozenset(
    {
        "pg_catalog",
        "information_schema",
        "pg_toast",
        "public",          # road_insight data lives only in road_insight schema
    }
)

# Glob-style prefixes whose matching tables must be rejected
FORBIDDEN_TABLE_PATTERNS: tuple[str, ...] = (
    "stg_",   # staging tables (always empty; excluded from LLM context)
    "pg_",    # system catalog
)

