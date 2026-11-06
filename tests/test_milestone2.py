"""
tests/test_milestone2.py
Milestone 2 test suite:
  - Database security & permission enforcement with roadinsight_readonly
  - Live query execution smoke tests on approved tables and views
  - Staging & data_sources access rejection tests
  - Streamlit UI chart generator unit tests
  - End-to-end live Text-to-SQL integration
"""
import pytest
import pandas as pd
from sqlalchemy import create_engine, text
from ai_analyst.config import settings
from ai_analyst.services.text_to_sql_service import run_text_to_sql
from dashboard.ai_analyst_tab import _create_chart, SUGGESTED_QUESTIONS


# ============================================================================
# 1. Database Security & Permission Tests (Live connection)
# ============================================================================

@pytest.fixture(scope="module")
def db_conn():
    """Fixture providing a live connection using roadinsight_readonly."""
    if not settings.db_configured:
        pytest.skip("READONLY_DATABASE_URL not configured")
    engine = create_engine(
        settings.readonly_database_url,
        connect_args={"options": "-csearch_path=road_insight,public"}
    )
    with engine.connect() as conn:
        yield conn


def test_db_role_identity(db_conn):
    """Verify user is strictly roadinsight_readonly."""
    row = db_conn.execute(text("SELECT current_user, session_user;")).fetchone()
    assert row[0] == "roadinsight_readonly"
    assert row[1] == "roadinsight_readonly"


def test_db_transaction_read_only(db_conn):
    """Verify session is in read-only mode."""
    row = db_conn.execute(text("SHOW transaction_read_only;")).fetchone()
    assert row[0].lower() in ("on", "true", "yes", "1")


def test_db_select_approved_tables(db_conn):
    """Verify SELECT works on key approved analytical tables."""
    tables = [
        "states",
        "cities",
        "state_annual_stats",
        "city_accident_stats",
        "city_violation_stats",
        "violation_type_stats",
        "collision_type_stats",
        "national_annual_stats",
    ]
    for tbl in tables:
        r = db_conn.execute(text(f"SELECT count(*) FROM road_insight.{tbl};")).fetchone()
        assert r[0] > 0, f"Table {tbl} should contain data"


def test_db_select_approved_7_views(db_conn):
    """Verify SELECT works on all 7 approved analytical views."""
    views = [
        "vw_state_yoy_comparison",
        "vw_national_trends",
        "vw_city_violation_summary",
        "vw_city_weather_summary",
        "vw_city_road_feature_summary",
        "vw_collision_type_summary",
        "vw_violation_type_summary",
    ]
    for v in views:
        r = db_conn.execute(text(f"SELECT count(*) FROM road_insight.{v};")).fetchone()
        assert r[0] > 0, f"View {v} should return rows"


def test_db_staging_tables_denied(db_conn):
    """Verify SELECT on staging tables is strictly denied."""
    with pytest.raises(Exception) as excinfo:
        db_conn.execute(text("SELECT * FROM road_insight.stg_large_cities;"))
    db_conn.rollback()
    assert "permission denied" in str(excinfo.value).lower()


def test_db_data_sources_denied(db_conn):
    """Verify SELECT on data_sources table is denied for read-only role."""
    with pytest.raises(Exception) as excinfo:
        db_conn.execute(text("SELECT * FROM road_insight.data_sources;"))
    db_conn.rollback()
    assert "permission denied" in str(excinfo.value).lower()


def test_db_dml_statements_denied(db_conn):
    """Verify write operations are completely blocked."""
    # INSERT
    with pytest.raises(Exception):
        db_conn.execute(text("INSERT INTO road_insight.states (state_name) VALUES ('X');"))
    db_conn.rollback()

    # UPDATE
    with pytest.raises(Exception):
        db_conn.execute(text("UPDATE road_insight.states SET is_active = false WHERE state_id = 1;"))
    db_conn.rollback()

    # DELETE
    with pytest.raises(Exception):
        db_conn.execute(text("DELETE FROM road_insight.states WHERE state_id = 1;"))
    db_conn.rollback()


# ============================================================================
# 2. UI Chart Generation Unit Tests
# ============================================================================

def test_chart_generator_bar():
    """Verify auto-generation of Plotly bar chart from valid dataframe."""
    df = pd.DataFrame({
        "state_name": ["Tamil Nadu", "Madhya Pradesh", "Kerala"],
        "accident_count": [67213, 55327, 48091]
    })
    fig = _create_chart(df, "bar")
    assert fig is not None
    assert len(fig.data) > 0


def test_chart_generator_line():
    """Verify auto-generation of Plotly line chart from time series dataframe."""
    df = pd.DataFrame({
        "year": [2019, 2020, 2021, 2022, 2023],
        "total_accidents": [456959, 372181, 412432, 461312, 480652]
    })
    fig = _create_chart(df, "line")
    assert fig is not None
    assert fig.data[0].type == "scatter"


def test_chart_generator_pie():
    """Verify auto-generation of Plotly pie chart from category dataframe."""
    df = pd.DataFrame({
        "violation_type_name": ["Over-speeding", "Wrong side", "Drunken driving"],
        "accident_count": [328727, 81999, 12256]
    })
    fig = _create_chart(df, "pie")
    assert fig is not None
    assert fig.data[0].type == "pie"


def test_chart_generator_empty_or_single_column():
    """Verify graceful handling when data is empty or single-column."""
    empty_df = pd.DataFrame()
    assert _create_chart(empty_df, "bar") is None

    single_col_df = pd.DataFrame({"count": [10, 20]})
    assert _create_chart(single_col_df, "bar") is None


def test_suggested_questions_validity():
    """Verify that all suggested questions are non-empty and formatted."""
    assert len(SUGGESTED_QUESTIONS) >= 6
    for q in SUGGESTED_QUESTIONS:
        assert isinstance(q, str)
        assert len(q) > 10


# ============================================================================
# 3. Live End-to-End Text-to-SQL Integration Test
# ============================================================================

def test_live_text_to_sql_execution():
    """Verify complete pipeline with live Groq call and live DB query execution."""
    if not settings.groq_configured or not settings.db_configured:
        pytest.skip("Groq or Database not configured")

    question = "Which are the top 3 states by road accidents in 2023?"
    response = run_text_to_sql(question)

    assert response.status == "success", f"Pipeline failed: {response.error}"
    assert response.sql is not None
    assert "road_insight.state_annual_stats" in response.sql
    assert response.data is not None
    assert len(response.data) == 3
    assert response.execution_time_ms > 0
    assert response.chart_type in ("bar", "table")
    assert len(response.explanation) > 10

