# Pytest Suite Full Execution & Verification Report

- **Execution Date:** 2026-11-12
- **Python Binary:** `DataEngineeringProject/.venv/bin/python3.13` (Python 3.13.1)
- **Pytest Version:** `pytest 9.2.0`
- **Execution Command:**
  ```bash
  cd DataEngineeringProject && PYTHONPATH=. .venv/bin/pytest -v --junitxml=docs/evidence/final_test_execution/junit_report.xml
  ```
- **Total Tests Collected:** 54
- **Passed:** **45**
- **Failed:** **0**
- **Skipped:** **9**
- **Errors:** **0**
- **Execution Time:** **2.08s**

---

## 1. Suite-by-Suite Breakdown

| Test File | Test Suite Focus | Framework / Type | Collected | Passed | Failed | Skipped | Status | Notes / Skip Reason |
|---|---|---|---|---|---|---|---|---|
| `tests/test_backend.py` | AI Analyst Backend Unit Tests | `pytest` / unit | 21 | 21 | 0 | 0 | **PASS** | Validated response parsing, AST security rules, DDL/DML blocking, connection failures, timeout handling. |
| `tests/test_dashboard_sql.py` | Dashboard Parameterization | `pytest` / integration | 2 | 1 | 0 | 1 | **PASS / SKIPPED** | `test_no_string_interpolation_in_dashboard_sql` passed; 1 test skipped: `DASHBOARD_DATABASE_URL` unreachable. |
| `tests/test_data_quality.py` | DQ Framework (R1-R6, Q1-Q8) | `unittest` / integration | 7 | 7 | 0 | 0 | **PASS** | Verified 14 automated checks in-memory. Q6 passed (100% additive). |
| `tests/test_etl.py` | Hardened Atomic ETL Loader | `unittest` / integration | 8 | 8 | 0 | 0 | **PASS** | Number parsing, decimal rejection, dry-run 1,299 rows, atomic rollback, and Annexure 45 regression test passed. |
| `tests/test_golden_accuracy.py` | Golden Query Evaluation (30 Qs) | `unittest` / evaluation | 2 | 2 | 0 | 0 | **PASS** | Evaluated 20 supported, 5 unsupported, 5 adversarial injection payloads. |
| `tests/test_milestone2.py` | Integration & Live End-to-End | `pytest` / live integration | 13 | 5 | 0 | 8 | **PASS / SKIPPED** | 5 chart generator & UI tests passed; 8 tests skipped: live DB / Groq network required (`@pytest.mark.skipif`). |
| `tests/test_no_secrets.py` | Static AST Secret Scanner | `pytest` / security | 1 | 1 | 0 | 0 | **PASS** | Scanned 128 tracked git files; 0 secrets or credential violations found. |
| **Total** | **Complete Project Suite** | **pytest + unittest** | **54** | **45** | **0** | **9** | **ALL RUNNABLE TESTS PASSED** | |

---

## 2. Analysis of the 9 Skipped Tests

All 9 skipped tests are intentionally decorated with `@pytest.mark.skipif` conditional guards that evaluate environment readiness:
1. `tests/test_dashboard_sql.py:test_dashboard_queries_executable_under_dashboard_role`: Skipped because `DASHBOARD_DATABASE_URL` is not set or local PostgreSQL port 5432 is offline.
2. `tests/test_milestone2.py:test_db_role_identity`: Skipped because `READONLY_DATABASE_URL` is offline.
3. `tests/test_milestone2.py:test_db_transaction_read_only`: Skipped because `READONLY_DATABASE_URL` is offline.
4. `tests/test_milestone2.py:test_db_select_approved_tables`: Skipped because `READONLY_DATABASE_URL` is offline.
5. `tests/test_milestone2.py:test_db_select_approved_7_views`: Skipped because `READONLY_DATABASE_URL` is offline.
6. `tests/test_milestone2.py:test_db_staging_tables_denied`: Skipped because `READONLY_DATABASE_URL` is offline.
7. `tests/test_milestone2.py:test_db_data_sources_denied`: Skipped because `READONLY_DATABASE_URL` is offline.
8. `tests/test_milestone2.py:test_db_dml_statements_denied`: Skipped because `READONLY_DATABASE_URL` is offline.
9. `tests/test_milestone2.py:test_live_text_to_sql_execution`: Skipped because `GROQ_API_KEY` is not configured.

---

## 3. Bug Fixes Applied During Test Verification
- **Fixed `tests/test_golden_accuracy.py`**: Updated property lookup from `val_res.is_valid` to `val_res.ok` to align with the `ValidationResult` dataclass in `ai_analyst/security/sql_validator.py`.
- **Added `pythonpath = .` to `pytest.ini`**: Ensures seamless module resolution for `ai_analyst` across test invocations.
- **Fixed `db_design/06_etl_loader.py:load_city_weather_stats`**: Added column whitespace normalisation (`df.columns = [re.sub(r'\s+', ' ', c).strip() for c in df.columns]`) resolving the Annexure 45 defect and bringing Check Q6 to 100% PASS.
- **Added Regression Test `test_annexure45_column_whitespace_stripped`**: Formally guards against regression in `tests/test_etl.py`.
- **Sanitized `docs/evidence/NOT_RUN.md`**: Fixed the open secret scanner violation, allowing `test_no_secrets.py` to pass with 0 violations.

