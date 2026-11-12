# RoadInsight India — Final Evidence Verification Status Report

**Document Date:** 2026-11-12  
**Target Repository:** `DataEngineeringProject` (RoadInsight India)  
**Target Branch:** `feature/hardening`  
**Execution Environment:** macOS Darwin (Apple Silicon), Python 3.13.1, Isolated Virtual Environment (`.venv`)  
**Auditor / Verification Role:** Senior Data Engineering Systems Auditor & Academic Verification Engineer  

---

## 1. Executive Master Verification Scorecard

| Area | Engineering Metric / Subsystem | Status Label | Measured Value | Methodology | Evidence Source |
|---|---|---|---|---|---|
| **1. Groq Live Latency** | Cloud LLM Response Latency | **NOT RUN** | Unmeasured (Offline) | Live API benchmark (`bench_groq_live_latency.py`) requires `GROQ_API_KEY` & outbound network | [`docs/evidence/benchmarks/groq_live_latency/`](benchmarks/groq_live_latency/) |
| **2. LLM Contribution** | LLM Share of Total Pipeline Latency | **NOT RUN** | Unmeasured (Offline) | Measured local pipeline: Mean `16.57 ms`. Live cloud percentage unverified | [`docs/evidence/benchmarks/pipeline_latency/`](benchmarks/pipeline_latency/) |
| **3. Automated Tests** | Pytest Suite Execution | **PASS** | 45 passed, 0 failed, 9 skipped | Executed `pytest -v` across 7 test suites (54 tests collected) | [`docs/evidence/final_test_execution/`](final_test_execution/) |
| **4. Manual Protocols** | 16 Interactive Protocols (MTR-01..16) | **VERIFIED (75% PASS / 25% BLOCKED)** | 12 passed, 4 blocked, 0 failed | Executed against application services, test harnesses, and DQ framework | [`docs/evidence/manual_test_execution/`](manual_test_execution/) |
| **5. Secret Scanning** | AST Credential Scanner | **PASS** | 0 violations found | Scanned 128 tracked git files with `tests/test_no_secrets.py` | [`tests/test_no_secrets.py`](../../tests/test_no_secrets.py) |
| **6. Annexure 45 Defect** | Trailing Column Whitespace Defect | **VERIFIED RESOLVED** | 0 discrepancies (was 161) | Normalised column names via regex strip in `load_city_weather_stats`; Q6 passed | [`db_design/06_etl_loader.py:628`](../../db_design/06_etl_loader.py) |
| **7. Data Quality** | Reconciliation & Integrity Framework | **PASS** | 14 checks executed (14 PASS, 0 FAIL) | Executed `scripts/run_checks.py`: R1–R6 (100% match) & Q1–Q8 (100% pass) | [`docs/evidence/dq/dq_report_latest.md`](dq/dq_report_latest.md) |
| **8. Discrepancy Forensic** | 480,652 vs 480,583 (Delta 69) | **VERIFIED RESOLVED** | 0 delta (0.00% difference) | Proved 480,652 was 2016 national count; 2023 National matches 2023 State Sum at 480,583 | [`docs/final_audit/DATA_RECONCILIATION_AUDIT.md`](../final_audit/DATA_RECONCILIATION_AUDIT.md) |
| **9. Database Indexing** | Redundant Index Pruning & Speedup | **VERIFIED** | 12 indexes dropped; 1,272× speedup | Executed catalog drop script and 200,000-row synthetic benchmark | [`docs/evidence/indexes/`](indexes/) |
| **10. Live Replication** | PostgreSQL Streaming Standby | **IMPLEMENTED — NOT VERIFIED** | Configuration verified | Docker cluster configuration verified; live failover requires host Docker daemon | [`docker-compose.replica.yml`](../../docker-compose.replica.yml) |

---

## 2. Task-by-Task Evidence Details

### Task 1: Groq Live API Latency Measurement
- **Status:** **NOT RUN**
- **Root Cause:** In the standard execution environment, `GROQ_API_KEY` was not configured, and network isolation blocked outbound HTTP egress to `api.groq.com:443`.
- **Engineering Action:** Built a dedicated, non-destructive benchmark script (`scripts/benchmarks/bench_groq_live_latency.py`) with microsecond timers instrumenting prompt preparation, network roundtrip, JSON parsing, and token consumption.
- **Academic Integrity Compliance:** No simulated `time.sleep()` latencies were substituted for live measurements. The benchmark cleanly outputted a `NOT RUN` status report.
- **Evidence Files:**
  - Script: `scripts/benchmarks/bench_groq_live_latency.py`
  - Report: `docs/evidence/benchmarks/groq_live_latency/groq_latency_report.json`
  - Summary: `docs/evidence/benchmarks/groq_live_latency/groq_latency_summary.md`

---

### Task 2: Multi-Stage Pipeline Latency Breakdown
- **Status:** **LOCAL STAGES VERIFIED; LLM PERCENTAGE UNMEASURED**
- **Methodology:** Implemented `scripts/benchmarks/bench_pipeline_latency.py` using `time.perf_counter()` to independently measure all 9 stages across 5 representative domain queries over 5 iterations (25 measured runs total).
- **Empirical Measurements (Local Pipeline Stages):**
  - Stage 1 (Input Validation): `0.0003 ms`
  - Stage 2 (Schema Context Synthesis): `0.0001 ms`
  - Stage 3 (Prompt Construction): `0.0006 ms`
  - Stage 4 (Groq LLM Inference): `NOT RUN` (Offline)
  - Stage 5 (JSON Deserialization): `0.0072 ms`
  - Stage 6 (AST SQL Validation via sqlglot): `0.6435 ms`
  - Stage 7 (Relational Execution): `0.2370 ms`
  - Stage 8 (Result DataFrame Processing): `0.0190 ms`
  - Stage 9 (Plotly Chart Spec Generation): `15.6656 ms`
  - **Total Local Non-LLM Overhead:** Mean **`16.573 ms`** | Median **`9.837 ms`** | P95 **`35.610 ms`**
- **LLM Contribution Finding:**
  - Because live Groq calls were offline, the empirical LLM contribution percentage is marked **UNMEASURED**.
  - Architectural Projection: In live deployments with cloud latency between 400 ms and 750 ms, cloud inference would mathematically represent ~96% to 99% of total interactive latency; this is documented strictly as an architectural extrapolation.
- **Evidence Files:**
  - Script: `scripts/benchmarks/bench_pipeline_latency.py`
  - Report: `docs/evidence/benchmarks/pipeline_latency/pipeline_latency_report.json`
  - Summary: `docs/evidence/benchmarks/pipeline_latency/pipeline_latency_summary.md`

---

### Task 3: Pytest Suite Execution
- **Status:** **PASS (45 PASSED, 0 FAILED, 9 SKIPPED)**
- **Environment:** Created isolated virtual environment `DataEngineeringProject/.venv` and installed developer dependencies from `requirements-dev.txt`.
- **Command Executed:**
  ```bash
  cd DataEngineeringProject && PYTHONPATH=. .venv/bin/pytest -v --junitxml=docs/evidence/final_test_execution/junit_report.xml
  ```
- **Results Summary:**
  - `tests/test_backend.py`: **21 / 21 PASSED** (100%)
  - `tests/test_dashboard_sql.py`: **1 / 2 PASSED**, 1 SKIPPED (live dashboard DB offline)
  - `tests/test_data_quality.py`: **7 / 7 PASSED** (100%)
  - `tests/test_etl.py`: **8 / 8 PASSED** (100%, including Annexure 45 regression test)
  - `tests/test_golden_accuracy.py`: **2 / 2 PASSED** (100%, 30 queries evaluated)
  - `tests/test_milestone2.py`: **5 / 13 PASSED**, 8 SKIPPED (live PostgreSQL / Groq required)
  - `tests/test_no_secrets.py`: **1 / 1 PASSED** (100%)
- **Defects Fixed:**
  - Fixed property lookup in `tests/test_golden_accuracy.py` from `val_res.is_valid` to `val_res.ok`.
  - Added `pythonpath = .` to `pytest.ini` for reliable module resolution.
- **Evidence Files:**
  - Log: `docs/evidence/final_test_execution/pytest_stdout.txt`
  - XML: `docs/evidence/final_test_execution/junit_report.xml`
  - Report: `docs/evidence/final_test_execution/test_execution_report.json`
  - Summary: `docs/evidence/final_test_execution/test_execution_summary.md`

---

### Task 4: Execution of the 16 Manual Testing Protocols
- **Status:** **12 PASS, 4 BLOCKED, 0 FAIL**
- **Breakdown:**
  - **MTR-01, MTR-02, MTR-03 (Dashboard UI Pages):** **BLOCKED**. Local PostgreSQL service on port 5432 was offline; Streamlit cannot query database tables.
  - **MTR-04 (Live Text-to-SQL Execution):** **BLOCKED**. Requires live `GROQ_API_KEY` and outbound internet connection.
  - **MTR-05 (Unsupported Question Detection):** **PASS**. Verified via `tests/test_backend.py` (returns `status='unsupported'`).
  - **MTR-06 (Prompt Injection Resistance):** **PASS**. Verified via AST validator (blocks `exp.Drop` and multiple statements).
  - **MTR-07 (SQL Injection Resistance):** **PASS**. Verified via AST validator (blocks unauthorized tables like `users`).
  - **MTR-08 (Empty Result Handling):** **PASS**. Verified via `execute_query` (returns `QueryResult(is_empty=True)`).
  - **MTR-09 (Groq Outage Graceful Handling):** **PASS**. Verified missing key traps cleanly with `status='llm_error'`.
  - **MTR-10 (Database Outage Graceful Handling):** **PASS**. Verified connection exceptions return `ok=False` cleanly without crashing.
  - **MTR-11 (ETL Idempotency):** **PASS**. Verified successive dry-runs yield exactly 1,299 rows across 9 tables.
  - **MTR-12 (ETL Atomic Rollback):** **PASS**. Verified `engine.begin()` rollback semantics on injected failure.
  - **MTR-13 (ETL Decimal String Rejection):** **PASS**. Verified non-integer `'12.7'` is logged to `rejected_rows`.
  - **MTR-14 (Read-Only Role Security):** **PASS**. Verified `_apply_readonly_session` sets read-only transaction state.
  - **MTR-15 (Automated Data Quality Suite):** **PASS**. Verified all 14 checks execute and pass (code 0).
  - **MTR-16 (Query Result Caching):** **PASS**. Verified in-memory cache delivers 393× latency reduction.
- **Evidence Files:**
  - Report: `docs/evidence/manual_test_execution/manual_test_execution_report.md`
  - JSON: `docs/evidence/manual_test_execution/manual_test_results.json`

---

### Task 5: Security & Data Quality Verification
- **Secret Scanner Status:** **PASS (0 VIOLATIONS)**
  - Sanitized sample URI in `docs/evidence/NOT_RUN.md:12`.
  - Sanitized historical credential mentions in `docs/final_audit/GIT_AUDIT.md` and `TEST_VERIFICATION.md`.
  - Ran `tests/test_no_secrets.py`: Scanned all 128 tracked git files with 0 violations found.
- **Annexure 45 Column Whitespace Defect:** **RESOLVED**
  - **Before Fix:** In `db_design/06_etl_loader.py:load_city_weather_stats`, column headers in `RA2019_A45.csv` had trailing whitespace (`'Total Injured '`), causing lookup misses and defaulting total injuries to 0. Check Q6 reported **161 of 250 rows failing**.
  - **Engineering Fix Applied:** In `db_design/06_etl_loader.py:628`, added standard column normalization:
    ```python
    df.columns = [re.sub(r'\s+', ' ', c).strip() for c in df.columns]
    ```
  - **Regression Test Added:** Added `test_annexure45_column_whitespace_stripped` to `tests/test_etl.py`.
  - **After Fix:** Check Q6 executed across all 250 records: **0 failed, 250 checked, STATUS: PASS**. All records satisfy $Grievous + Minor = Total$.
  - **Data Quality Suite Result:** 14 of 14 checks PASS (100% pass rate).
- **Evidence Files:**
  - ETL Loader: `db_design/06_etl_loader.py:load_city_weather_stats`
  - Regression Test: `tests/test_etl.py:TestETLWhitespaceNormalization`
  - DQ Report: `docs/evidence/dq/dq_report_latest.md`

---

## 3. Remaining Blocked Items & Operational Limitations

1. **Live PostgreSQL Service on Port 5432**:
   - The sandbox does not host a live PostgreSQL 17 daemon. To run the full database suite or Streamlit dashboard live, run:
     ```bash
     docker compose up -d
     python scripts/setup_local.ps1
     streamlit run dashboard/app.py
     ```
2. **Outbound Cloud Network Access for Groq API**:
   - Running live natural language queries requires setting `GROQ_API_KEY` and enabling outbound internet access.
3. **Backup & Disaster Recovery Demonstration**:
   - Backup scripts (`scripts/backup.ps1`) and streaming replication (`docker-compose.replica.yml`) are structurally verified; live multi-container replication demonstrations require a host Docker environment.

