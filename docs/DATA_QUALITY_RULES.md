# RoadInsight India — Data Quality Rules and Transformation Specifications

## Overview
This document defines the formal data cleansing, validation, rejection, and integrity rules enforced by the RoadInsight India data engineering pipeline. Every rule is programmatically enforced in `db_design/06_etl_loader.py` and validated through `scripts/run_checks.py`.

---

## 1. Zero vs NULL Semantics (Daman & Diu Case Study)

### Background: UT Merger (2020)
Under the *Dadra and Nagar Haveli and Daman and Diu (Merger of Union Territories) Act, 2019*, effective 26 January 2020, the separate Union Territories of:
1. **Dadra and Nagar Haveli**
2. **Daman and Diu**

were formally merged into a single administrative unit: **Dadra & Nagar Haveli and Daman & Diu**.

### Source Data Phenomenon
In the raw MoRTH accident datasets (`RoadStateWiseAcc.csv` and `RoadStatewiseKilled.csv`):
- **Pre-2020 (e.g. 2019)**:
  - `Daman & Diu`: 69 accidents, 28 fatalities.
  - `Dadra & Nagar Haveli*`: 68 accidents, 49 fatalities.
- **Post-2020 Transition (e.g. 2022)**:
  - `Daman & Diu`: `0` accidents reported, but `NaN` fatalities.
  - `Dadra & Nagar Haveli*`: `196` accidents, `90` fatalities (reflecting consolidated reporting).
- **2023**:
  - `Daman & Diu`: `NaN` accidents, `NaN` fatalities.
  - `Dadra & Nagar Haveli*`: `182` accidents, `74` fatalities.

### Data Quality Enforcement Rule
1. **`0` (Zero)**: Represents an **explicit count of zero** recorded and certified by the reporting jurisdiction. It is preserved strictly as `0` in integer columns and MUST NOT be coerced to `NULL`.
2. **`NULL`**: Represents **missing, unreported, or consolidated data** where no specific reporting occurred for that territory individually. It MUST NOT be imputed as `0`, because treating missing data as zero artificially distorts national aggregates and average fatality rate calculations.
3. **Audit Trail**: Any coercion from empty strings or sentinel tokens (`'-'`, `'NA'`) to `NULL` increments the `null_coerced` metric in `road_insight.etl_run_log`.

---

## 2. Numeric Parsing and Decimal Rejection

### Rule 2.1: Integer Count Fields
All accident, killed, and injured metrics in fact tables are integer counters.
- **Valid Formatting**:
  - Standard integers: `456959`, `'456959'`
  - Indian comma grouping: `'4,56,959'` -> `456959`
  - Floating integer equivalents: `'12.0'`, `12.0` -> `12`
- **Rejection of Non-Integer Decimals**:
  - If a metric contains a genuine non-integer decimal (e.g., `'12.7'`, `12.7`), the pipeline **does not silently truncate** to `12` (which was a previous defect).
  - The row is rejected with `reason = 'non_integer_value'` and recorded in `road_insight.rejected_rows` with the raw input JSON.

### Rule 2.2: Rate and Percentage Fields
- Columns like `accidents_pct_change`, `fatalities_per_10k_vehicles`, and `population_thousands` accept valid floating-point numbers.
- Sentinel tokens (`'-'`, `'NA'`, `'N/A'`, `'#N/A'`) are safely coerced to `NULL`.

---

## 3. Entity Name Normalization

### City Name Canonicalization
Source files contain historical spelling variations and parenthetical disambiguations. The canonical mappings applied prior to dimension lookup:
- `'allahabad (prayagraj)'` / `'allahabad(prayagraj)'` -> `'Allahabad (Prayagraj)'`
- `'khozikode'` -> `'Kozhikode'`
- `'mallapuram'` -> `'Malappuram'`
- `'thiruvanthapuram'` -> `'Thiruvananthapuram'`
- `'vijaywada city'` -> `'Vijayawada'`
- `'vizaq'` -> `'Visakhapatnam'`
- `'vadodra'` -> `'Vadodara'`

### State Name Canonicalization
- `'j & k #'` / `'j & k'` -> `'Jammu & Kashmir'`
- `'dadra & nagar haveli*'` -> `'Dadra & Nagar Haveli and Daman & Diu'`

---

## 4. Pipeline Execution & Idempotency

### Single-Transaction Atomicity
The entire load across all 9 target tables executes within a single database transaction (`engine.begin()`). If an error or constraint violation occurs at any point:
- All staged changes and table deletes roll back automatically.
- No partial or corrupted state remains in the database.
- The master run record in `road_insight.etl_run_log` is marked `status = 'FAILED'`.

### Audit and Lineage Tracking
- Every loaded record carries a valid foreign key `source_id` referencing `road_insight.data_sources`.
- Every ETL run records:
  - Total rows read, loaded, rejected, and null-coerced in `road_insight.etl_run_log`.
  - Exact per-table timings and counts in `road_insight.etl_run_table_log`.
  - Full diagnostic JSON payloads for rejected rows in `road_insight.rejected_rows`.

