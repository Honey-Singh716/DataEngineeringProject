"""
tests/test_backend.py
Comprehensive test suite for the Road Insight AI Analyst backend.

Covers all 20 required verification scenarios:
  1. Groq response parsing
  2. Successful SQL generation
  3. Unsupported questions handling
  4. Invalid JSON response handling
  5. Multiple SQL statements rejection
  6. INSERT rejection
  7. DELETE rejection
  8. DROP rejection
  9. Unauthorized table access rejection
  10. Staging table access rejection
  11. Unauthorized schema access rejection
  12. Dangerous function calls rejection
  13. CTE validation (allowed vs data-modifying)
  14. Subquery validation
  15. Missing LIMIT enforcement
  16. Empty query results handling
  17. Database connection failure handling
  18. Query timeout handling
  19. Read-only transaction safety
  20. Complete Text-to-SQL workflow
"""
import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from sqlalchemy.exc import OperationalError

from ai_analyst.security.sql_validator import validate_sql
from ai_analyst.llm.sql_generator import _parse_response, generate_sql
from ai_analyst.database.query_executor import execute_query, QueryResult
from ai_analyst.services.text_to_sql_service import run_text_to_sql
from ai_analyst.config import settings


# ============================================================================
# 1. Groq response parsing
# ============================================================================
def test_groq_response_parsing_valid():
    raw_json = '''{
        "status": "success",
        "sql": "SELECT state_name, accident_count FROM road_insight.state_annual_stats sas JOIN road_insight.states s ON sas.state_id = s.state_id WHERE sas.year = 2023 ORDER BY sas.accident_count DESC NULLS LAST LIMIT 5;",
        "explanation": "Retrieves the top 5 states by accident count in 2023.",
        "chart_type": "bar",
        "confidence": "high"
    }'''
    parsed = _parse_response(raw_json, "Top 5 states in 2023")
    assert parsed.status == "success"
    assert "road_insight.state_annual_stats" in parsed.sql
    assert parsed.chart_type == "bar"
    assert parsed.confidence == "high"
    assert len(parsed.parse_errors) == 0


# ============================================================================
# 2. Successful SQL generation (Mocked LLM)
# ============================================================================
@patch("ai_analyst.llm.sql_generator.call_groq")
def test_successful_sql_generation(mock_call_groq):
    mock_call_groq.return_value = '''{
        "status": "success",
        "sql": "SELECT COUNT(*) FROM road_insight.cities;",
        "explanation": "Counts total cities in the database.",
        "chart_type": "table",
        "confidence": "high"
    }'''
    res = generate_sql("How many cities are there?")
    assert res.is_success
    assert res.sql == "SELECT COUNT(*) FROM road_insight.cities;"
    assert res.chart_type == "table"


# ============================================================================
# 3. Unsupported questions
# ============================================================================
def test_unsupported_question_handling():
    raw_json = '''{
        "status": "unsupported",
        "sql": null,
        "explanation": "District-level data is not available in the database.",
        "chart_type": null,
        "confidence": "high"
    }'''
    parsed = _parse_response(raw_json, "Accidents in Mysore district?")
    assert parsed.is_unsupported
    assert parsed.sql is None
    assert "District-level data is not available" in parsed.explanation


# ============================================================================
# 4. Invalid JSON response handling
# ============================================================================
def test_invalid_json_response_handling():
    invalid_raw = "I'm sorry, I cannot output JSON right now: SELECT * FROM states"
    parsed = _parse_response(invalid_raw, "Some question")
    assert parsed.status == "unsupported"
    assert parsed.sql is None
    assert len(parsed.parse_errors) > 0


# ============================================================================
# 5. Multiple SQL statements rejection
# ============================================================================
def test_multiple_sql_statements_rejected():
    sql = "SELECT * FROM road_insight.states; SELECT * FROM road_insight.cities;"
    res = validate_sql(sql)
    assert not res.ok
    assert any("Exactly one SQL statement is allowed" in err for err in res.errors)


# ============================================================================
# 6. INSERT rejection
# ============================================================================
def test_insert_rejected():
    sql = "INSERT INTO road_insight.states (state_name) VALUES ('NewState');"
    res = validate_sql(sql)
    assert not res.ok
    assert any("Only SELECT" in err or "Disallowed SQL operation" in err for err in res.errors)


# ============================================================================
# 7. DELETE rejection
# ============================================================================
def test_delete_rejected():
    sql = "DELETE FROM road_insight.states WHERE state_id = 1;"
    res = validate_sql(sql)
    assert not res.ok
    assert any("Only SELECT" in err or "Disallowed SQL operation" in err for err in res.errors)


# ============================================================================
# 8. DROP rejection
# ============================================================================
def test_drop_rejected():
    sql = "DROP TABLE road_insight.states CASCADE;"
    res = validate_sql(sql)
    assert not res.ok
    assert any("Only SELECT" in err or "Disallowed SQL operation" in err for err in res.errors)


# ============================================================================
# 9. Unauthorized table access
# ============================================================================
def test_unauthorized_table_rejected():
    sql = "SELECT * FROM road_insight.user_passwords;"
    res = validate_sql(sql)
    assert not res.ok
    assert any("not in the approved analytical table allowlist" in err for err in res.errors)


# ============================================================================
# 10. Staging table access rejection
# ============================================================================
def test_staging_table_rejected():
    sql = "SELECT * FROM road_insight.stg_large_cities;"
    res = validate_sql(sql)
    assert not res.ok
    assert any("staging table" in err.lower() for err in res.errors)


# ============================================================================
# 11. Unauthorized schema access
# ============================================================================
def test_unauthorized_schema_rejected():
    sql = "SELECT * FROM pg_catalog.pg_tables;"
    res = validate_sql(sql)
    assert not res.ok
    assert any("forbidden" in err.lower() for err in res.errors)


# ============================================================================
# 12. Dangerous function calls rejection
# ============================================================================
def test_dangerous_function_rejected():
    sql = "SELECT pg_sleep(10);"
    res = validate_sql(sql)
    assert not res.ok
    assert any("Dangerous function 'pg_sleep'" in err for err in res.errors)

    sql2 = "SELECT pg_read_file('server.key');"
    res2 = validate_sql(sql2)
    assert not res2.ok
    assert any("Dangerous function 'pg_read_file'" in err for err in res2.errors)


# ============================================================================
# 13. CTE validation (allowed vs data-modifying)
# ============================================================================
def test_valid_cte_allowed():
    sql = """
    WITH state_totals AS (
        SELECT state_id, SUM(accident_count) AS total_acc
        FROM road_insight.state_annual_stats
        GROUP BY state_id
    )
    SELECT s.state_name, st.total_acc
    FROM state_totals st
    JOIN road_insight.states s ON st.state_id = s.state_id
    LIMIT 10;
    """
    res = validate_sql(sql)
    assert res.ok
    assert res.sql is not None

def test_data_modifying_cte_rejected():
    sql = """
    WITH deleted_rows AS (
        DELETE FROM road_insight.state_annual_stats RETURNING *
    )
    SELECT * FROM deleted_rows;
    """
    res = validate_sql(sql)
    assert not res.ok
    assert any("Data-modifying CTE" in err or "Disallowed SQL operation" in err for err in res.errors)


# ============================================================================
# 14. Subquery validation
# ============================================================================
def test_subquery_with_unauthorized_table_rejected():
    sql = """
    SELECT * FROM road_insight.states 
    WHERE state_id IN (SELECT state_id FROM road_insight.stg_road_state_acc);
    """
    res = validate_sql(sql)
    assert not res.ok
    assert any("staging table" in err.lower() for err in res.errors)


# ============================================================================
# 15. Missing LIMIT enforcement
# ============================================================================
def test_missing_limit_enforced():
    sql = "SELECT state_name FROM road_insight.states;"
    res = validate_sql(sql, max_rows=100)
    assert res.ok
    assert "LIMIT 100" in res.sql
    assert len(res.warnings) > 0


# ============================================================================
# 16. Empty query results handling
# ============================================================================
@patch("ai_analyst.database.query_executor.get_readonly_engine")
def test_empty_query_results_handled(mock_get_engine):
    mock_conn = MagicMock()
    mock_result = MagicMock()
    mock_result.fetchmany.return_value = []
    mock_result.keys.return_value = ["state_name", "accident_count"]
    
    mock_conn.begin.return_value.__enter__.return_value = None
    mock_conn.execute.return_value = mock_result
    mock_engine = MagicMock()
    mock_engine.connect.return_value.__enter__.return_value = mock_conn
    mock_get_engine.return_value = mock_engine

    qr = execute_query("SELECT state_name, accident_count FROM road_insight.state_annual_stats WHERE year = 1800;")
    assert qr.ok
    assert qr.is_empty
    assert qr.row_count == 0
    assert list(qr.data.columns) == ["state_name", "accident_count"]


# ============================================================================
# 17. Database connection failure handling
# ============================================================================
@patch("ai_analyst.database.query_executor.get_readonly_engine")
def test_database_connection_failure_handled(mock_get_engine):
    mock_get_engine.side_effect = RuntimeError("READONLY_DATABASE_URL is not configured.")
    qr = execute_query("SELECT 1;")
    assert not qr.ok
    assert "READONLY_DATABASE_URL is not configured" in qr.error


# ============================================================================
# 18. Query timeout handling
# ============================================================================
@patch("ai_analyst.database.query_executor.get_readonly_engine")
def test_query_timeout_handled(mock_get_engine):
    mock_conn = MagicMock()
    mock_conn.begin.return_value.__enter__.return_value = None
    # Simulate statement timeout from postgres
    mock_conn.execute.side_effect = OperationalError("statement timeout occurred", None, Exception("canceling statement due to statement timeout"))
    mock_engine = MagicMock()
    mock_engine.connect.return_value.__enter__.return_value = mock_conn
    mock_get_engine.return_value = mock_engine

    qr = execute_query("SELECT * FROM road_insight.state_annual_stats;")
    assert not qr.ok
    assert "timed out after" in qr.error.lower()


# ============================================================================
# 19. Read-only transaction enforcement in connection module
# ============================================================================
def test_readonly_transaction_enforcement_event():
    from ai_analyst.database.connection import _apply_readonly_session
    mock_cursor = MagicMock()
    mock_dbapi = MagicMock()
    mock_dbapi.cursor.return_value = mock_cursor

    _apply_readonly_session(mock_dbapi, None)

    # Verify SET default_transaction_read_only = on was called
    executed_statements = [call[0][0] for call in mock_cursor.execute.call_args_list]
    assert any("default_transaction_read_only = on" in stmt for stmt in executed_statements)
    assert any("statement_timeout" in stmt for stmt in executed_statements)


# ============================================================================
# 20. Complete Text-to-SQL workflow
# ============================================================================
@patch("ai_analyst.llm.sql_generator.call_groq")
@patch("ai_analyst.services.text_to_sql_service.execute_query")
@patch.object(settings, "readonly_database_url", "postgresql://roadinsight_readonly:valid_pass@localhost:5432/roadinsight")
def test_complete_text_to_sql_workflow(mock_execute, mock_call_groq):
    mock_call_groq.return_value = '''{
        "status": "success",
        "sql": "SELECT s.state_name, sas.accident_count FROM road_insight.state_annual_stats sas JOIN road_insight.states s ON sas.state_id = s.state_id WHERE sas.year = 2023 ORDER BY sas.accident_count DESC NULLS LAST LIMIT 5;",
        "explanation": "Retrieves the top 5 states by road accident count in 2023.",
        "chart_type": "bar",
        "confidence": "high"
    }'''

    df_sample = pd.DataFrame({
        "state_name": ["Tamil Nadu", "Madhya Pradesh", "Kerala", "Uttar Pradesh", "Karnataka"],
        "accident_count": [67213, 55425, 48141, 44534, 43448]
    })
    mock_execute.return_value = QueryResult(
        ok=True,
        data=df_sample,
        row_count=5,
        execution_time_ms=12.5,
        is_empty=False
    )

    response = run_text_to_sql("Which are the top 5 states by road accidents in 2023?")
    assert response.status == "success"
    assert response.sql is not None
    assert response.data is not None
    assert response.row_count == 5
    assert response.chart_type == "bar"
    assert response.data.iloc[0]["state_name"] == "Tamil Nadu"
    assert response.error is None
