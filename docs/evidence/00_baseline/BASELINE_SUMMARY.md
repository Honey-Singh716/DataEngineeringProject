# Phase 0: Baseline & Environment Audit Report

**Project:** Road Insight India (Data Engineering Project)  
**Branch:** `feature/hardening`  
**Date:** 2026-11-11  
**Status:** COMPLETE (All baseline metrics & bug reproductions verified)

---

## 1. Environment & Infrastructure Baseline

All measurements taken directly on the host development machine:

| Component | Measured Value | Evidence Source |
|---|---|---|
| **Operating System** | Windows 11 Pro (Build 10.0.26200, AMD64) | [`environment_info.txt`](./environment_info.txt) |
| **CPU Architecture** | 12 Logical Cores (Intel64 Family 6 Model 186) | [`environment_info.json`](./environment_info.json) |
| **System RAM** | 7.71 GB Total (0.71 GB Available during baseline run) | [`environment_info.json`](./environment_info.json) |
| **Python Version** | Python 3.13.13 | [`environment_info.txt`](./environment_info.txt) |
| **PostgreSQL Version** | PostgreSQL 17.10 on x86_64-windows (msvc-19.44.35226, 64-bit) | [`environment_info.txt`](./environment_info.txt) |
| **PG Shared Buffers** | 128 MB | [`environment_info.txt`](./environment_info.txt) |
| **PG Max Connections** | 100 | [`environment_info.txt`](./environment_info.txt) |

---

## 2. Test Suite Inventory Baseline (`pytest`)

Before applying any code modifications, the existing test suite was cataloged and executed:

- **Total Tests:** 34 tests across 2 test modules.
- **Status:** **34 Passed, 0 Failed, 0 Skipped** (when database and Groq API are reachable).
- **Execution Time:** 5.63 seconds.
- **Evidence Files:** [`pytest_baseline.txt`](./pytest_baseline.txt), [`pytest_inventory.txt`](./pytest_inventory.txt).

### Test Breakdown by Category

1. **Unit & Security Tests (Mocked API):** `tests/test_backend.py` (21 tests)
   - Config loading & Pydantic settings.
   - Groq singleton client instantiation & backoff logic.
   - SQL generator JSON schema parsing and error handling.
   - SQLGlot AST validator: single-statement enforcement, DDL/DML rejection, schema qualification, table allowlist enforcement, system catalog access rejection, auto-LIMIT injection.
   - Schema context verification across all 15 approved analytical tables.
2. **Integration & Frontend Verification:** `tests/test_milestone2.py` (13 tests)
   - 7 live database role least-privilege verification tests against `roadinsight_readonly`.
   - 1 live Groq LLM Text-to-SQL end-to-end execution test (`test_live_text_to_sql_execution`).
   - 5 UI, session-state, and chart-rendering component tests.

---

## 3. Database Table Inventory & Row Counts

Measured via PostgreSQL `information_schema.tables` and `pg_total_relation_size`:

- **Total Base Tables in Schema `road_insight`:** 21 tables.
- **Total Rows Stored:** 1,424 rows.
- **Total Table Storage:** ~1,392 KB.
- **Evidence Files:** [`table_row_counts.txt`](./table_row_counts.txt), [`table_row_counts.csv`](./table_row_counts.csv).

| Table Name | Category | Row Count | Relation Size | Notes |
|---|---|---|---|---|
| `states` | Dimension | 37 | 64.0 KB | 36 active states/UTs + 1 inactive (Daman & Diu) |
| `cities` | Dimension | 50 | 72.0 KB | MoRTH 50 million-plus cities |
| `violation_types` | Dimension | 6 | 48.0 KB | Primary violation categories |
| `collision_types` | Dimension | 9 | 48.0 KB | Collision classification categories |
| `road_features` | Dimension | 8 | 48.0 KB | Infrastructure feature types |
| `weather_conditions` | Dimension | 5 | 48.0 KB | Weather classification categories |
| `data_sources` | Metadata | 10 | 32.0 KB | Data provenance catalog for 10 CSV files |
| `national_historical_stats` | Fact | 29 | 56.0 KB | 1970–2019 historical time series |
| `national_annual_stats` | Fact | 5 | 56.0 KB | 2019–2023 annual national metrics |
| `state_annual_stats` | Fact | 185 | 168.0 KB | 37 states × 5 years |
| `city_accident_stats` | Fact | 100 | 120.0 KB | 50 cities × 2 years (2022–2023) |
| `city_violation_stats` | Fact | 300 | 144.0 KB | 50 cities × 6 violation types (2023) |
| `city_weather_stats` | Fact | 250 | 144.0 KB | 50 cities × 5 weather types (2019) |
| `city_road_feature_stats` | Fact | 400 | 152.0 KB | 50 cities × 8 road features (2019) |
| `collision_type_stats` | Fact | 18 | 72.0 KB | 9 collision types × 2 years (2022–2023) |
| `violation_type_stats` | Fact | 12 | 72.0 KB | 6 violation types × 2 years (2022–2023) |
| `stg_large_cities` | Staging | 0 | 16.0 KB | Reserved staging table (unused by Python ETL) |
| `stg_large_cities_vio` | Staging | 0 | 16.0 KB | Reserved staging table (unused by Python ETL) |
| `stg_road_no_acc` | Staging | 0 | 16.0 KB | Reserved staging table (unused by Python ETL) |
| `stg_road_state_acc` | Staging | 0 | 16.0 KB | Reserved staging table (unused by Python ETL) |
| `stg_road_state_killed` | Staging | 0 | 16.0 KB | Reserved staging table (unused by Python ETL) |

---

## 4. Index Catalog & Size Baseline

Cataloged via `pg_index`, `pg_class`, and `pg_relation_size`:

- **Total Indexes in Schema `road_insight`:** 68 indexes.
- **Total Index Storage:** 1,088.0 KB (16 KB per index).
- **Evidence Files:** [`pg_indexes.txt`](./pg_indexes.txt), [`pg_indexes.csv`](./pg_indexes.csv).

---

## 5. Bug Reproduction Suite Results (`repro_bugs.py`)

Every suspected defect identified in evaluation feedback was empirically verified before any changes were made.
Evidence file: [`repro_bugs.txt`](./repro_bugs.txt).

| Bug ID | Suspected Defect | Empirical Result | Detailed Evidence |
|---|---|---|---|
| **B2** | `roadinsight_readonly` cannot SELECT from `vw_state_stats_full` & `vw_city_stats_full` | **PASS (Bug Present)** | PostgreSQL raises `InsufficientPrivilege: permission denied for view vw_state_stats_full` because underlying `data_sources` table is not granted to role. |
| **B3** | `dashboard/app.py::get_engine` raises on localhost URLs | **PASS (Bug Present)** | Code explicitly executes `if "localhost" in database_url or "127.0.0.1" in database_url: raise RuntimeError(...)`. |
| **B5** | ETL loaders lack overarching atomic transaction | **PASS (Bug Present)** | `main()` in `06_etl_loader.py` calls loaders sequentially without an overarching `engine.begin()`; exceptions midway leave database half-committed. |
| **B6** | `load_road_no_acc` uses positional indexing & leaves `pct_cols` unused | **PASS (Bug Present)** | `row.iloc[2]`, `row.iloc[4]`, `row.iloc[6]` are hardcoded while `pct_cols` is computed on every row and never referenced. |
| **B7** | ETL silently drops invalid rows and truncates decimals in `parse_indian_number` | **PASS (Bug Present)** | `parse_indian_number("12.7")` returns integer `12` (silent truncation via `int(float(s))`), and rows with `year_val is None` are skipped via `continue` without logging. |
| **B9** | Redundant indexes exist in schema | **PASS (Bug Present)** | 5 candidate redundant indexes (`idx_nat_hist_year`, `idx_nat_ann_year`, `idx_state_stats_state_year`, `idx_city_acc_city_year`, `idx_city_vio_city_year_type`) verified active alongside duplicate unique constraint indexes. |

---

## 6. Deliverables Created in Phase 0

1. **Git Branch:** `feature/hardening` created from clean `main`.
2. **Dependencies:** `requirements-dev.txt` created with `-r requirements.txt`, `pytest-cov`, `matplotlib`, `psutil`.
3. **Containerization:** `docker-compose.yml` added for PostgreSQL 17 service with persistent volume.
4. **Documentation:** `README.md` updated with comprehensive Windows local setup guide (both Docker & Non-Docker paths).
5. **PowerShell Automation:** `scripts/setup_local.ps1` implemented with secure password handling.
6. **Bug Reproduction Harness:** `scripts/repro_bugs.py` created and executed.
7. **Baseline Evidence Directory:** Complete baseline evidence generated under `docs/evidence/00_baseline/`.

