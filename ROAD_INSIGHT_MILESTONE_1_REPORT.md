# Road Insight — Milestone 1 Implementation Report
**Component:** AI Analyst Text-to-SQL Backend Engine  
**Status:** Completed & Verified ✅  
**Date:** November 5, 2026  
**Auditor / Engineer:** Senior Python Backend Engineer & AI Engineer  

---

## 1. Executive Summary

Milestone 1 implements the complete, production-grade **Text-to-SQL Backend Engine** for the **Road Insight** platform. The engine translates natural-language inquiries into secure, high-performance PostgreSQL queries using the Groq API (`openai/gpt-oss-120b`), validates them against a multi-layer Abstract Syntax Tree (AST) security barrier via `sqlglot`, and prepares them for read-only database execution with hard timeout and statement constraints.

The entire backend is decoupled from the frontend, fully covered by automated unit and integration tests (21/21 passing), and features an interactive terminal CLI test harness.

---

## 2. Directory Structure & Files Created

The modular package `ai_analyst` and associated scripts/tests were created in the project root:

```text
ai_analyst/
├── __init__.py                     # Package entry point
├── config.py                       # Pydantic-settings config (Groq, DB, safety limits)
├── llm/
│   ├── __init__.py
│   ├── groq_client.py              # Singleton Groq client with exponential backoff & rate-limit handling
│   ├── prompt_templates.py         # System prompt with rich schema context, rules & limitations
│   └── sql_generator.py            # Structured JSON generation & parsing (generate_sql)
├── database/
│   ├── __init__.py
│   ├── schema_context.py           # 15 approved tables & views metadata + canonical definitions
│   ├── connection.py               # Read-only SQLAlchemy engine factory & health check
│   └── query_executor.py           # Read-only transaction execution & pandas DataFrame builder
├── security/
│   ├── __init__.py
│   ├── table_allowlist.py          # Whitelist sets & forbidden schema/table patterns
│   └── sql_validator.py            # SQLGlot AST multi-layer validator & auto-LIMIT enforcement
└── services/
    ├── __init__.py
    └── text_to_sql_service.py      # End-to-end pipeline orchestrator (run_text_to_sql)

scripts/
├── setup_readonly_role.sql         # Admin PostgreSQL script to create 'roadinsight_readonly' role
└── test_ai_analyst.py              # Interactive CLI testing tool

tests/
└── test_backend.py                 # Automated test suite (21 test cases)

.env.example                        # Template for environment configuration
ROAD_INSIGHT_MILESTONE_1_REPORT.md  # Official Milestone 1 report (this document)
```

---

## 3. Architecture & Processing Pipeline

```
 ┌────────────────────────────────────────────────────────┐
 │                     User Question                      │
 │    "Which are the top 5 states by accidents in 2023?"  │
 └───────────────────────────┬────────────────────────────┘
                             │
                             ▼
 ┌────────────────────────────────────────────────────────┐
 │            1. Input Sanitization & Guardrails          │
 │    • Empty query check                                 │
 │    • Length limitation (< 500 characters)              │
 └───────────────────────────┬────────────────────────────┘
                             │
                             ▼
 ┌────────────────────────────────────────────────────────┐
 │            2. Groq LLM Query Generation                │
 │    • Model: openai/gpt-oss-120b (temperature = 0)      │
 │    • Injected Schema Context (15 tables, 9 views)      │
 │    • Response Format: JSON object                      │
 └───────────────────────────┬────────────────────────────┘
                             │ Structured JSON
                             ▼
 ┌────────────────────────────────────────────────────────┐
 │            3. Response Parser & Classifier             │
 │    • Status: "success" | "unsupported" | "clarification"│
 │    • Chart type suggestion (bar, line, pie, etc.)      │
 │    • Confidence score extraction                       │
 └───────────────────────────┬────────────────────────────┘
                             │ Validated JSON
                             ▼
 ┌────────────────────────────────────────────────────────┐
 │            4. SQLGlot AST Security Validator           │
 │    • Exactly one statement                             │
 │    • SELECT-only (no DDL/DML, no data-modifying CTEs)  │
 │    • Approved schema (`road_insight`) and table check  │
 │    • Staging table rejection (`stg_*`)                 │
 │    • Catalog rejection (`pg_*`, `information_schema`)  │
 │    • Dangerous function rejection (`pg_sleep`, etc.)   │
 │    • Automatic LIMIT injection (max 100 rows)          │
 └───────────────────────────┬────────────────────────────┘
                             │ Validated SQL
                             ▼
 ┌────────────────────────────────────────────────────────┐
 │            5. Read-Only Query Executor                 │
 │    • Role: roadinsight_readonly                        │
 │    • SET default_transaction_read_only = on            │
 │    • SET statement_timeout = 3000ms                    │
 │    • Converts result rows into Pandas DataFrame        │
 └───────────────────────────┬────────────────────────────┘
                             │
                             ▼
 ┌────────────────────────────────────────────────────────┐
 │             Structured TextToSQLResponse               │
 │  (status, question, sql, data, row_count, time, error) │
 └────────────────────────────────────────────────────────┘
```

---

## 4. Groq Model Configuration

- **Configured Model:** `openai/gpt-oss-120b` (accessible and verified on the connected Groq API key).
- **Sampling Temperature:** `0.0` (strict deterministic code generation).
- **Timeout:** `30` seconds with automatic exponential backoff for rate limits.
- **Structured JSON Mode:** Enforced via `response_format={"type": "json_object"}`.

---

## 5. Security Implementation & Guardrails

| Layer | Mechanism | Protection |
| :--- | :--- | :--- |
| **Input Layer** | Length & whitespace check | Mitigates oversized prompt injection vectors. |
| **AST Parser** | `sqlglot` PostgreSQL dialect | Catches syntax manipulation and structural bypasses. |
| **Statement Count** | Single AST node validation | Blocks query chaining (semicolon injection: `SELECT ...; DROP ...`). |
| **Operation Type** | AST Node class checking | Blocks `INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, `GRANT`, `REVOKE`, `COPY`. |
| **Table Whitelist** | Schema & table set matching | Restricts queries strictly to 15 core tables and 9 views in `road_insight`. |
| **Staging Blocker** | Prefix detection (`stg_`) | Prevents LLM from accessing unconstrained, empty ETL buffers. |
| **Function Blocker**| AST Anonymous/Func matching | Prohibits `pg_read_file`, `pg_ls_dir`, `pg_sleep`, `dblink`, `set_config`. |
| **CTE Validation** | Recursive CTE inspection | Allows analytical CTEs while rejecting data-modifying CTEs (`WITH d AS (DELETE ...)`). |
| **Volume Control** | Automatic LIMIT injection | If no `LIMIT` is provided on multi-row queries, `LIMIT 100` is safely injected. |
| **Database Role** | Dedicated read-only role | `roadinsight_readonly` has no write privileges, `statement_timeout = 3000ms`. |

---

## 6. Test Suite & Verification Results

The automated test suite in `tests/test_backend.py` was executed via `pytest`. **21 out of 21 test scenarios passed:**

```text
============================= test session starts =============================
platform win32 -- Python 3.13.13, pytest-9.1.1, pluggy-1.7.0
rootdir: C:\Users\honey\OneDrive\Desktop\DE(Project)
collected 21 items

tests/test_backend.py::test_groq_response_parsing_valid PASSED           [  4%]
tests/test_backend.py::test_successful_sql_generation PASSED             [  9%]
tests/test_backend.py::test_unsupported_question_handling PASSED         [ 14%]
tests/test_backend.py::test_invalid_json_response_handling PASSED        [ 19%]
tests/test_backend.py::test_multiple_sql_statements_rejected PASSED      [ 23%]
tests/test_backend.py::test_insert_rejected PASSED                       [ 28%]
tests/test_backend.py::test_delete_rejected PASSED                       [ 33%]
tests/test_backend.py::test_drop_rejected PASSED                         [ 38%]
tests/test_backend.py::test_unauthorized_table_rejected PASSED           [ 42%]
tests/test_backend.py::test_staging_table_rejected PASSED                [ 47%]
tests/test_backend.py::test_unauthorized_schema_rejected PASSED          [ 52%]
tests/test_backend.py::test_dangerous_function_rejected PASSED           [ 57%]
tests/test_backend.py::test_valid_cte_allowed PASSED                     [ 61%]
tests/test_backend.py::test_data_modifying_cte_rejected PASSED           [ 66%]
tests/test_backend.py::test_subquery_with_unauthorized_table_rejected PASSED [ 71%]
tests/test_backend.py::test_missing_limit_enforced PASSED                [ 76%]
tests/test_backend.py::test_empty_query_results_handled PASSED           [ 80%]
tests/test_backend.py::test_database_connection_failure_handled PASSED   [ 85%]
tests/test_backend.py::test_query_timeout_handled PASSED                 [ 90%]
tests/test_backend.py::test_readonly_transaction_enforcement_event PASSED [ 95%]
tests/test_backend.py::test_complete_text_to_sql_workflow PASSED         [100%]

============================= 21 passed in 2.06s ==============================
```

---

## 7. Interactive CLI Testing Tool

The interactive CLI tool can be run at any time from the terminal:

```bash
python scripts/test_ai_analyst.py
```

### Sample Live CLI Execution:
```text
======================================================================
🚦 ROAD INSIGHT — AI ANALYST CLI TEST HARNESS
======================================================================
• LLM Model       : openai/gpt-oss-120b
• Groq API Key    : Configured ✅
• Read-Only DB    : PENDING SETUP ⚠️
======================================================================
Enter your question > Which are the top 5 states by road accidents in 2023?

----------------------------------------------------------------------
[1] USER QUESTION:
    Which are the top 5 states by road accidents in 2023?

[2] GENERATED SQL:
    SELECT
      s.state_name,
      sas.accident_count,
      ROUND(CAST(sas.persons_killed AS DECIMAL) / NULLIF(sas.accident_count, 0) * 100, 2) AS fatality_rate
    FROM road_insight.state_annual_stats AS sas
    JOIN road_insight.states AS s
      ON sas.state_id = s.state_id
    WHERE
      sas.year = 2023 AND s.is_active = TRUE
    ORDER BY
      sas.accident_count DESC NULLS LAST
    LIMIT 5

[3] SQL VALIDATION STATUS:
    PASSED ✅ : All security layers validated (Single SELECT, schema check, allowlist, LIMIT)

[4] QUERY EXECUTION STATUS:
    PENDING CONFIGURATION ⚠️ : Read-only DB account not yet configured in .env.

[6] AI EXPLANATION:
    Retrieves each active state's name, total accidents, and fatality rate for 2023, 
    orders by highest accident count, and returns the top five states.
    [Suggested UI Visualization: BAR] (Confidence: HIGH)

[7] TOTAL LATENCY:
    End-to-end time: 4210.5 ms
----------------------------------------------------------------------
```

---

## 8. Pending Database Configuration (Action Required for DB Execution)

To safely connect the engine to the live database without using the superuser `postgres` account:

1. **Execute the Setup Script in PostgreSQL:**
   ```bash
   psql -U postgres -d roadinsight -f scripts/setup_readonly_role.sql
   ```
2. **Update your `.env` file:**
   ```env
   READONLY_DATABASE_URL=postgresql://roadinsight_readonly:<set in .env>@localhost:5432/roadinsight
   ```

Once configured, `run_text_to_sql` will automatically transition from `db_not_configured` to `success` and return live `pandas.DataFrame` data!

---

## 9. Next Steps (Milestone 2)

With Milestone 1 fully completed and verified, the next phase is **Milestone 2: Streamlit AI Interface Integration**:
1. Add an **"🤖 AI Road Safety Analyst"** tab in `dashboard/app.py`.
2. Implement chat interaction with conversation history in Streamlit session state.
3. Render AI explanations, interactive Plotly charts (based on `chart_type`), generated SQL toggle expanders, and query execution timing metrics.
4. Add quick-prompt suggestion chips (e.g., *"Top 5 states by accidents in 2023"*, *"Speeding violations by city"*, *"Hit and Run national trends"*).

