"""
tests/test_dashboard_sql.py
Tests for SQL statements in dashboard/app.py:
1. Static AST analysis: asserts zero string interpolation (no f-strings, %, or .format()).
2. Database execution: executes every query under the roadinsight_dashboard role
   to ensure all permissions and bound parameters work properly.
"""

from __future__ import annotations

import ast
import os
from pathlib import Path
import pytest
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
APP_PY_PATH = PROJECT_ROOT / "dashboard" / "app.py"
load_dotenv(PROJECT_ROOT / ".env")


def extract_queries_from_app_ast() -> list[dict]:
    """Parse app.py and extract all calls to query(engine, sql, params)."""
    assert APP_PY_PATH.exists(), f"File {APP_PY_PATH} not found"
    tree = ast.parse(APP_PY_PATH.read_text(encoding="utf-8"))
    
    extracted = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func_name = getattr(node.func, "id", getattr(node.func, "attr", ""))
            if func_name == "query":
                assert len(node.args) >= 2, f"query() called with fewer than 2 arguments at line {node.lineno}"
                sql_arg = node.args[1]
                
                # Check for string interpolation anti-patterns
                is_fstring = isinstance(sql_arg, ast.JoinedStr)
                is_binop = isinstance(sql_arg, ast.BinOp) and isinstance(sql_arg.op, ast.Mod)
                is_str_format = (
                    isinstance(sql_arg, ast.Call)
                    and getattr(sql_arg.func, "attr", "") == "format"
                )
                
                has_interpolation = is_fstring or is_binop or is_str_format
                sql_text = sql_arg.value if isinstance(sql_arg, ast.Constant) else None
                
                # Check if third argument (params) is passed
                has_params = len(node.args) >= 3 or any(kw.arg == "params" for kw in node.keywords)
                
                extracted.append({
                    "line": node.lineno,
                    "has_interpolation": has_interpolation,
                    "is_constant": isinstance(sql_arg, ast.Constant),
                    "sql_text": sql_text,
                    "has_params": has_params
                })
    return extracted


def test_no_string_interpolation_in_dashboard_sql():
    """Verify via AST that all SQL queries in app.py are plain constants with bound parameters."""
    queries = extract_queries_from_app_ast()
    assert len(queries) > 0, "No query() calls found in app.py"
    
    violations = [
        f"Line {q['line']}: query contains string interpolation (f-string or format)"
        for q in queries if q["has_interpolation"] or not q["is_constant"]
    ]
    assert not violations, "Found string interpolation in dashboard SQL:\n" + "\n".join(violations)


def test_dashboard_queries_executable_under_dashboard_role():
    """Verify that all dashboard queries execute successfully under roadinsight_dashboard role."""
    dash_url = (
        os.getenv("DASHBOARD_DATABASE_URL")
        or os.getenv("DATABASE_URL")
        or "postgresql://roadinsight_dashboard:DashPass123!Safe@localhost:5432/roadinsight"
    )
    
    try:
        engine = create_engine(dash_url)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as e:
        pytest.skip(f"Database not accessible under roadinsight_dashboard: {e}")
    
    queries = extract_queries_from_app_ast()
    assert len(queries) > 0
    
    # Sample parameter sets for parameterized queries
    sample_params = {
        "year": 2023,
        "city": "Delhi"
    }
    
    failures = []
    with engine.connect() as conn:
        for q in queries:
            sql = q["sql_text"]
            assert sql is not None
            try:
                # Execute with sample parameters where applicable
                res = pd.read_sql(text(sql), conn, params=sample_params)
                assert isinstance(res, pd.DataFrame)
            except Exception as e:
                failures.append(f"Line {q['line']} failed under roadinsight_dashboard: {e}")
                
    assert not failures, "Dashboard queries failed under roadinsight_dashboard role:\n" + "\n".join(failures)

