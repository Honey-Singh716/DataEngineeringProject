# Road Insight — Milestone 2 Implementation Report
**Component:** AI Analyst Frontend & Live Database Integration  
**Status:** Completed, Verified & Passing (34/34 Tests) ✅  
**Date:** November 5, 2026  
**Auditor / Engineer:** Senior Python Backend Engineer & AI Engineer  

---

## 1. Executive Summary

Milestone 2 delivers the full, end-to-end user-facing capability of the **Road Insight AI Analyst**:
1. **Frontend Integration:** A dedicated **"🤖 AI Analyst"** page integrated directly into the existing Streamlit dashboard (`dashboard/app.py` via `dashboard/ai_analyst_tab.py`), maintaining all 6 original analytical pages without any regression.
2. **Interactive UI Features:** Natural-language chat input, conversation history in Streamlit session state, 6 pre-built one-click suggested questions, SQL transparency expanders with execution stats, interactive dark-themed Plotly charts (bar, line, pie), and instant CSV data export.
3. **Database Security Verification:** 100% verified against the live PostgreSQL 17.10 database using the unprivileged `roadinsight_readonly` role. All write and DDL operations are blocked, staging tables and metadata tables (`data_sources`) are blocked, and strict read-only transactions with a 3-second statement timeout are enforced.
4. **Testing & Performance:** 34/34 automated tests passing across backend security, AST validation, live database permissions, auto-chart generation, and end-to-end live Text-to-SQL query generation. Lightweight design optimized for 8 GB RAM systems with zero overhead.

---

## 2. Files Created & Modified

### Files Created:
- **`dashboard/ai_analyst_tab.py`**: Modular Streamlit component rendering the AI Analyst chat interface, suggested questions, SQL transparency expander, auto-chart generator, and data viewer.
- **`scripts/verify_readonly_security.py`**: Automated audit script testing 12 distinct security constraints on the `roadinsight_readonly` connection.
- **`tests/test_milestone2.py`**: Automated test suite (13 tests) covering live database permissions, view accessibility, chart generation, and live Text-to-SQL execution.
- **`requirements.txt`**: Consolidated, minimal dependency manifest.
- **`ROAD_INSIGHT_MILESTONE_2_REPORT.md`**: Official Milestone 2 certification report (this file).

### Files Modified:
- **`dashboard/app.py`**: Added `"🤖 AI Analyst"` to the sidebar navigation and routed to `render_ai_analyst_page()` without altering existing dashboard code.
- **`ai_analyst/database/schema_context.py`**: Restricted `ALLOWED_TABLES` to strictly approved analytical tables and 7 approved views; excluded `data_sources`, `vw_state_stats_full`, and `vw_city_stats_full`.
- **`scripts/setup_readonly_role.sql`**: Updated to follow strict least-privilege principles (explicit grants on approved tables only, removed broad `ALL TABLES` grants and `ALTER DEFAULT PRIVILEGES`).

---

## 3. Architecture & End-to-End Request Flow

```
┌────────────────────────────────────────────────────────────────────────┐
│                        STREAMLIT WEB INTERFACE                         │
│   • Suggested question button OR User natural language input           │
│   • Chat history rendered via st.session_state                         │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                      ai_analyst Pipeline Service                       │
│                   (run_text_to_sql in text_to_sql_service.py)          │
└───────────────────┬───────────────────────────────┬────────────────────┘
                    │                               │
                    ▼                               ▼
    ┌──────────────────────────────┐ ┌───────────────────────────────────┐
    │       Groq API Client        │ │      SQLGlot AST Validator        │
    │   Model: openai/gpt-oss-120b │ │   • Single SELECT enforcement     │
    │   Temperature: 0.0           │ │   • Approved schema & tables      │
    │   Structured JSON format     │ │   • Staging & catalog rejection   │
    │   Schema Context injected    │ │   • Automatic LIMIT 100 injection │
    └──────────────────────────────┘ └───────────────────────────────────┘
                                                    │
                                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                    PostgreSQL 17.10 Database                           │
│   • Role: roadinsight_readonly                                         │
│   • SET default_transaction_read_only = on                             │
│   • SET statement_timeout = '3000ms'                                   │
│   • Returns real analytical rows (Pandas DataFrame)                    │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                    Rich Streamlit UI Visualization                     │
│   • Plain-English AI explanation                                       │
│   • Interactive Plotly chart (auto-detected: bar, line, pie)           │
│   • Expandable SQL viewer with latency & row counts                    │
│   • Paginated interactive DataFrame table                              │
│   • One-click CSV download                                             │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Database Security Verification Results

Security audit executed via `scripts/verify_readonly_security.py` directly against the live PostgreSQL database using the `roadinsight_readonly` credentials:

| # | Security Check | Status | Verification Detail |
| :- | :--- | :---: | :--- |
| 1 | **Role Identity** | **PASS** | Connected as `roadinsight_readonly` to database `roadinsight`. |
| 2 | **No Elevated Privileges** | **PASS** | `rolsuper=False`, `rolcreaterole=False`, `rolcreatedb=False`. |
| 3 | **Read-Only Session** | **PASS** | `transaction_read_only` confirmed `on`. |
| 4 | **Approved Table SELECT** | **PASS** | `SELECT count(*)` on `state_annual_stats` succeeded (185 rows). |
| 5 | **Staging Table Access** | **PASS** | `SELECT` on `stg_large_cities` rejected (`permission denied`). |
| 6 | **INSERT Rejection** | **PASS** | Blocked with `cannot execute INSERT in a read-only transaction`. |
| 7 | **UPDATE Rejection** | **PASS** | Blocked with `cannot execute UPDATE in a read-only transaction`. |
| 8 | **DELETE Rejection** | **PASS** | Blocked with `cannot execute DELETE in a read-only transaction`. |
| 9 | **DROP Rejection** | **PASS** | Blocked with `cannot execute DROP TABLE in a read-only transaction`. |
| 10 | **CREATE Rejection** | **PASS** | Blocked with `cannot execute CREATE TABLE in a read-only transaction`. |
| 11 | **Approved 7 Views** | **PASS** | All 7 views operational (`vw_state_yoy_comparison`, `vw_national_trends`, `vw_city_violation_summary`, `vw_city_weather_summary`, `vw_city_road_feature_summary`, `vw_collision_type_summary`, `vw_violation_type_summary`). |
| 12 | **Metadata Protection** | **PASS** | `data_sources` table access properly denied (`permission denied`). |

**Audit Result:** 12/12 security checks passed. Zero privilege leaks detected.

---

## 5. Automated Test Suite Execution (34/34 Passing)

All tests across unit, security, and live integration passed:

```text
============================= test session starts =============================
platform win32 -- Python 3.13.13, pytest-9.1.1, pluggy-1.7.0
rootdir: C:\Users\honey\OneDrive\Desktop\DE(Project)
collected 34 items

tests/test_backend.py::test_groq_response_parsing_valid PASSED           [  2%]
tests/test_backend.py::test_successful_sql_generation PASSED             [  5%]
tests/test_backend.py::test_unsupported_question_handling PASSED         [  8%]
tests/test_backend.py::test_invalid_json_response_handling PASSED        [ 11%]
tests/test_backend.py::test_multiple_sql_statements_rejected PASSED      [ 14%]
tests/test_backend.py::test_insert_rejected PASSED                       [ 17%]
tests/test_backend.py::test_delete_rejected PASSED                       [ 20%]
tests/test_backend.py::test_drop_rejected PASSED                         [ 23%]
tests/test_backend.py::test_unauthorized_table_rejected PASSED           [ 26%]
tests/test_backend.py::test_staging_table_rejected PASSED                [ 29%]
tests/test_backend.py::test_unauthorized_schema_rejected PASSED          [ 32%]
tests/test_backend.py::test_dangerous_function_rejected PASSED           [ 35%]
tests/test_backend.py::test_valid_cte_allowed PASSED                     [ 38%]
tests/test_backend.py::test_data_modifying_cte_rejected PASSED           [ 41%]
tests/test_backend.py::test_subquery_with_unauthorized_table_rejected PASSED [ 44%]
tests/test_backend.py::test_missing_limit_enforced PASSED                [ 47%]
tests/test_backend.py::test_empty_query_results_handled PASSED           [ 50%]
tests/test_backend.py::test_database_connection_failure_handled PASSED   [ 52%]
tests/test_backend.py::test_query_timeout_handled PASSED                 [ 55%]
tests/test_backend.py::test_readonly_transaction_enforcement_event PASSED [ 58%]
tests/test_backend.py::test_complete_text_to_sql_workflow PASSED         [ 61%]
tests/test_milestone2.py::test_db_role_identity PASSED                   [ 64%]
tests/test_milestone2.py::test_db_transaction_read_only PASSED           [ 67%]
tests/test_milestone2.py::test_db_select_approved_tables PASSED          [ 70%]
tests/test_milestone2.py::test_db_select_approved_7_views PASSED         [ 73%]
tests/test_milestone2.py::test_db_staging_tables_denied PASSED           [ 76%]
tests/test_milestone2.py::test_db_data_sources_denied PASSED             [ 79%]
tests/test_milestone2.py::test_db_dml_statements_denied PASSED           [ 82%]
tests/test_milestone2.py::test_chart_generator_bar PASSED                [ 85%]
tests/test_milestone2.py::test_chart_generator_line PASSED               [ 88%]
tests/test_milestone2.py::test_chart_generator_pie PASSED                [ 91%]
tests/test_milestone2.py::test_chart_generator_empty_or_single_column PASSED [ 94%]
tests/test_milestone2.py::test_suggested_questions_validity PASSED       [ 97%]
tests/test_milestone2.py::test_live_text_to_sql_execution PASSED         [100%]

============================= 34 passed in 5.52s ==============================
```

---

## 6. How to Run the Application & Access AI Analyst

### Step 1: Ensure PostgreSQL Service is Running
Make sure local PostgreSQL is active on port 5432.

### Step 2: Launch Streamlit
Execute the following command in the project root:

```powershell
streamlit run dashboard/app.py
```

### Step 3: Access the AI Analyst
1. The app will open in your browser at `http://localhost:8501`.
2. In the left sidebar, navigate to the new tab: **`🤖 AI Analyst`**.
3. Click any of the **6 suggested questions** or type any question into the chat input at the bottom.

---

## 7. Sample Queries & Verified Live Responses

### Sample 1: Ranking Query
- **Question:** *"Which are the top 5 states by road accidents in 2023?"*
- **Generated SQL:**
  ```sql
  SELECT
    s.state_name,
    sas.accident_count
  FROM road_insight.state_annual_stats AS sas
  JOIN road_insight.states AS s
    ON sas.state_id = s.state_id
  WHERE
    sas.year = 2023 AND s.is_active = TRUE
  ORDER BY
    sas.accident_count DESC NULLS LAST
  LIMIT 5
  ```
- **Live Output:**
  - Tamil Nadu: 67,213
  - Madhya Pradesh: 55,327
  - Kerala: 48,091
  - Uttar Pradesh: 44,534
  - Karnataka: 43,440
- **Visualization:** Interactive Horizontal Bar Chart with Road Insight cyan/blue theme.

### Sample 2: Trend Query
- **Question:** *"Show national accident trends from 2019 to 2023."*
- **Generated SQL:**
  ```sql
  SELECT
    year,
    total_accidents,
    total_fatalities
  FROM road_insight.national_annual_stats
  ORDER BY year ASC
  LIMIT 100
  ```
- **Visualization:** Line Chart showing dip in 2020 (lockdown) and recovery through 2023.

### Sample 3: Out-of-Scope Query
- **Question:** *"Which district in Karnataka had the most accidents?"*
- **Response:**
  - Status: `unsupported`
  - Explanation: *"The database schema does not contain any district-level data, only state, city, and national level tables. Therefore district-level accident information cannot be retrieved."*
  - Helpful suggestion rendered automatically guiding user back to supported state/city queries.

---

## 8. Known Analytical Limitations

Users asking questions beyond the dataset boundaries will receive clear, helpful domain explanations:
1. **No District-Level Data:** Only State/UT level and 50 designated million-plus cities are present.
2. **Annual Granularity Only:** No monthly, weekly, daily, or hourly timestamps exist.
3. **Environmental Data Year Boundaries:**
   - Weather condition statistics are available for **2019 only**.
   - Road feature geometry statistics are available for **2019 only**.
   - City violation cause breakdown is available for **2023 only**.
4. **No State Population Denominators:** Per-capita rates cannot be computed for individual states (only national historical population is available).

---

## 9. Conclusion

Milestone 2 is **100% complete**. The Road Insight dashboard now features a state-of-the-art, secure, AI-powered natural-language Text-to-SQL analyst with full SQL transparency, live database execution, and interactive visual analytics.

