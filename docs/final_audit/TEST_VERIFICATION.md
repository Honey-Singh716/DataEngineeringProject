# RoadInsight India — Test Suite Verification & Audit Report

**Auditor Role:** Senior QA / Backend Verification Engineer  
**Audit Date:** 2026-11-11  
**Repository:** `DataEngineeringProject` (RoadInsight India)  
**Execution Environment:** macOS Darwin, Python 3.13.1 (Sandboxed Read-Only Mode)  

---

## 1. Test Suite Inventory & Execution Matrix

| Test Suite / File | Test Framework | Marker / Tier | Declared Tests | Executed in Audit | Passed | Failed / Errored | Skipped | Status | Root Cause / Audit Finding |
|---|---|---|---|---|---|---|---|---|---|
| `tests/test_etl.py` | `unittest` | `integration` | 7 | 7 | 7 | 0 | 0 | **PASS (VERIFIED)** | Validated number parsing, non-integer rejection, null coercion, dry-run across 9 loaders, atomic rollback. |
| `tests/test_data_quality.py` | `unittest` | `integration` | 7 | 7 | 7 | 0 | 0 | **PASS (VERIFIED)** | Validated R1-R6 reconciliation and Q1-Q8 data quality checks in-memory. |
| `tests/test_golden_accuracy.py` | `unittest` | `unit`, `live` | 2 | 2 | 2 | 0 | 0 | **PASS (VERIFIED)** | Evaluated all 30 golden evaluation queries (20 supported, 5 unsupported, 5 adversarial). |
| `tests/test_no_secrets.py` | Custom / Pytest | `unit` | 1 | 1 | 0 | 1 | 0 | **FAIL (ACTIVE DEFECT FOUND)** | Found 1 violation in `docs/evidence/NOT_RUN.md:12`: contains literal `postgres:postgres@localhost`. |
| `tests/test_dashboard_sql.py` | `pytest` | `integration` | 3 | 0 | 0 | 3 (ImportError) | 0 | **BLOCKED (ENVIRONMENT)** | Requires `pytest` package from `requirements-dev.txt` (not installed in system Python). |
| `tests/test_backend.py` | `pytest` | `unit` | 21 | 0 | 0 | 21 (ImportError) | 0 | **BLOCKED (ENVIRONMENT)** | Requires `pytest` and `sqlglot` from `requirements-dev.txt`. |
| `tests/test_milestone2.py` | `pytest` | `integration` | 13 | 0 | 0 | 13 (ImportError) | 0 | **BLOCKED (ENVIRONMENT)** | Requires `pytest` from `requirements-dev.txt`. |

---

## 2. Execution Log & Reproducible Commands

### Command 1: Standard Library Test Execution (ETL, DQ, Golden)
```bash
python3 -m unittest tests/test_etl.py tests/test_data_quality.py tests/test_golden_accuracy.py -v
```
- **Exit Code**: `0` (Success)
- **Ran**: 16 tests in 0.132s
- **Results**: 16 passed, 0 failed, 0 errors.

### Command 2: Secret Scanning Audit
```bash
python3 -c "import tests.test_no_secrets as s; s.test_no_hardcoded_secrets_in_tracked_files()"
```
- **Exit Code**: `1` (AssertionError)
- **Finding**: Detected 1 hardcoded connection string with default credentials:
  ```text
  AssertionError: Found 1 secret/credential violations in tracked files:
  docs/evidence/NOT_RUN.md:12 - Connection URI contains credential for user 'postgres'
  ```
- **Remediation Required**: In `docs/evidence/NOT_RUN.md`, replace `postgresql://<user>:<password>@localhost:5432` with `<sanitized_placeholder>` to adhere to the strict zero-secret policy.

### Command 3: Pytest Suite Execution
```bash
pytest -v
```
- **Execution Status**: **NOT RUN IN SANDBOX (ENVIRONMENT DEPENDENCY)**
- **Reason**: The developer machine environment requires installing developer dependencies:
  ```powershell
  pip install -r requirements-dev.txt
  ```
  In this sandbox environment, `pytest` is not present in the global `/Library/Frameworks/Python.framework/Versions/3.13` site-packages.

---

## 3. Detailed Verification of Test Logic

### 3.1 `tests/test_etl.py` (7 Tests)
- `test_valid_indian_numbers`: Verifies `'4,56,959'` -> `456959`, `'12.0'` -> `12`.
- `test_null_coercion`: Verifies `'NA'`, `'-'`, `''`, `None` coerce to `None` and increment `null_coerced`.
- `test_non_integer_rejection`: Verifies non-integer string `'12.7'` does not silently truncate to `12`, but is rejected with `reason = 'non_integer_value'`.
- `test_city_normalization`: Canonical city name mapping.
- `test_state_normalization`: Canonical state name mapping.
- `test_dry_run_full_pipeline`: Executes all 9 loaders against real source CSVs; confirms 1,299 rows loaded with 0 unhandled errors.
- `test_atomic_rollback_on_loader_error`: Simulates loader write failure; verifies exception propagation and status marking.

### 3.2 `tests/test_data_quality.py` (7 Tests)
- `test_all_14_checks_executed`: Ensures R1–R6 and Q1–Q8 are all evaluated.
- `test_r1_reconciliation`: Verifies 5-year mathematical match between state sums and national totals.
- `test_r3_r4_totals`: Verifies collision and violation type sums equal national annual figures.
- `test_q1_referential_integrity`: Verifies 0 orphan foreign keys.
- `test_q2_duplicate_uniqueness`: Verifies 0 duplicate natural keys.
- `test_q4_mandatory_non_null`: Verifies no missing primary dimensions.
- `test_q6_upstream_discrepancy_documented`: Captures the known check status.

### 3.3 `tests/test_golden_accuracy.py` (2 Tests, 30 Queries)
- `test_all_30_queries_present`: Confirms exactly 20 supported, 5 unsupported, 5 adversarial.
- `test_golden_queries_evaluation`: Evaluates reference SQL syntax, injection blocking, and out-of-scope rejection, exporting to `docs/evidence/golden/golden_results.csv`.

