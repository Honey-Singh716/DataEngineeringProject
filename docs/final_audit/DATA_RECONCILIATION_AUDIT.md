# RoadInsight India — Data Reconciliation & Mathematical Discrepancy Audit

**Auditor Role:** Senior Data Quality & Forensic Data Auditor  
**Audit Date:** 2026-11-11  
**Target Branch:** `feature/hardening`  

---

## 1. Executive Summary: Resolving Key Contradictions

During this independent engineering audit, three prominent numerical contradictions and data anomalies across project documentation were forensically traced back to their raw source CSV files, ETL parsing logic, and SQL aggregations:

1. **The "480,652 vs 480,583 (Difference of 69)" Mystery**:
   - **Finding**: **RESOLVED & PROVEN AS A FALSE HISTORICAL DISCREPANCY**.
   - An earlier manual guide reported a 69-accident discrepancy between National and State totals, attributing it to Daman & Diu.
   - **Root Cause**: The author conflated the **2016** National accident count (`480,652` from `DataSets/RA2019_A1.csv`) with the **2023** State sum (`480,583` from `Data/RoadStateWiseAcc.csv`). The difference $480,652 - 480,583 = 69$ happened to match Daman & Diu's **2019** accident count (69), causing false speculation.
   - **Empirical Reality**: Comparing the same year (2023), National Total is **480,583** and State Sum is **480,583**. The actual discrepancy is **0 (0.00% delta)**.

2. **The "161 Non-Additive Injury Records in RA2019_A45.csv" Anomaly**:
   - **Finding**: **RESOLVED AS AN ETL COLUMN WHITESPACE BUG (NOT A GOVERNMENT DATA DEFECT)**.
   - Project documentation and check Q6 claimed that the MoRTH official report has 161 non-additive injury records.
   - **Root Cause**: In `DataSets/RA2019_A45.csv`, the column header has a trailing space (`'Sunny/Clear - Persons Injured - Total Injured '`). In `06_etl_loader.py:661`, the loader searched for `'Sunny/Clear - Persons Injured - Total Injured'` without stripping column whitespace, causing `row.get()` to default to `0`.
   - **Empirical Reality**: When trailing whitespace is properly stripped from column names, **0 out of 250 records exhibit discrepancies**; the government data is 100% mathematically additive ($Grievous + Minor = Total$).

3. **Daman & Diu 2020 Administrative Merger & Zero vs NULL Semantics**:
   - **Finding**: **VERIFIED AS LEGITIMATE ADMINISTRATIVE CONSOLIDATION**.
   - Under the 2020 UT merger, Daman & Diu's reporting was integrated into Dadra & Nagar Haveli.
   - Explicit `0` (recorded zero accidents in 2022) is correctly preserved distinct from `NULL` (unreported in 2023) to avoid distorting analytical averages.

---

## 2. Forensic Traceability: The 480,652 vs 480,583 Discrepancy

### Evidence Trace:
1. **`DataSets/RA2019_A1.csv` (Line 27)**:
   ```csv
   2016,480652,150785,494624,1268961,230031,5603293,...
   ```
   National total accidents in **2016** was **480,652**.
2. **`Data/RoadNoAcc.csv` (Line 6)**:
   ```csv
   2023,"4,80,583",4.2,"1,72,890",2.6,"4,62,825",4.4
   ```
   National total accidents in **2023** was **480,583**.
3. **`Data/RoadStateWiseAcc.csv` (State rows for 2023)**:
   Sum of all 37 states and UTs in **2023** equals **480,583**.
4. **`Data/RoadStateWiseAcc.csv` (Line 32, Daman & Diu)**:
   ```csv
   31,Daman & Diu,69,67,46,0,
   ```
   Daman & Diu accidents in **2019** was **69**.
5. **`tests/test_milestone2.py` (Line 134)**:
   ```python
   "total_accidents": [456959, 372181, 412432, 461312, 480652]
   ```
   A previous developer hardcoded `480652` as the mock value for 2023 instead of `480583`.

### Audit Conclusion:
The claim that there was a 69-accident discrepancy in 2023 between National and State data was an error in the previous manual documentation. The raw MoRTH 2023 datasets match with 100.00% precision:
$$\text{National Total (2023)} = 480,583 = \sum \text{State Accidents (2023)}$$
$$\text{Delta} = 0 \quad (0.00\%)$$

---

## 3. Forensic Traceability: The 161 Injury Discrepancies in Annexure 45

### Evidence Trace:
1. **Raw Source Inspection (`DataSets/RA2019_A45.csv`)**:
   Inspecting exact column headers in Python:
   ```python
   >>> [c for c in df.columns if 'Total Injured' in c]
   ['Sunny/Clear - Persons Injured - Total Injured ',
    'Rainy - Persons Injured - Total Injured ',
    'Foggy and Misty - Persons Injured - Total Injured ',
    'Hail/Sleet - Persons Injured - Total Injured ',
    'Others - Persons Injured - Total Injured ']
   ```
   *Notice the trailing space at the end of each header string!*

2. **ETL Loader Code (`db_design/06_etl_loader.py:661`)**:
   ```python
   total_col = f'{prefix} - Persons Injured - Total Injured'  # Missing trailing space!
   ```
   Because `df.columns = [c.strip() for c in df.columns]` was omitted in `load_city_weather_stats`, `row.get(total_col, 0)` failed to match the CSV column and returned the default `0`.

3. **Check Q6 Execution in `scripts/run_checks.py:426`**:
   ```python
   diff_mask = cws['persons_grievously_injured'] + cws['persons_minor_injured'] != cws['persons_total_injured']
   ```
   Because `persons_total_injured` was loaded as `0`, for every city-weather record where `minor_injured > 0` or `grievously_injured > 0` (161 out of 250 records), the check evaluated:
   $$\text{Grievous} + \text{Minor} \ne 0 \implies \text{True (Failed)}$$
   The remaining 89 records had 0 grievous and 0 minor injuries ($0 + 0 = 0$), passing by pure coincidence.

### Audit Conclusion:
The 161 non-additive records reported in `DATA_QUALITY_RULES.md` and check Q6 was **an ETL column name whitespace defect**, NOT an upstream government data discrepancy. When the column names have whitespace stripped, the MoRTH 2019 Annexure 45 report has **0 discrepancies across all 250 records**.

---

## 4. Reconciliation Verification Across All 5 Years (R1 Check)

Reconciling `national_annual_stats` (`RoadNoAcc.csv`) against $\sum \text{state\_annual\_stats}$ (`RoadStateWiseAcc.csv`):

| Year | National Total Accidents | Sum of 37 States / UTs | Delta (Difference) | Reconciliation % | Audit Status |
|---|---|---|---|---|---|
| **2019** | 456,959 | 456,959 | 0 | 100.00% (0.00% diff) | **VERIFIED PERFECT** |
| **2020** | 372,181 | 372,181 | 0 | 100.00% (0.00% diff) | **VERIFIED PERFECT** |
| **2021** | 412,432 | 412,432 | 0 | 100.00% (0.00% diff) | **VERIFIED PERFECT** |
| **2022** | 461,312 | 461,312 | 0 | 100.00% (0.00% diff) | **VERIFIED PERFECT** |
| **2023** | 480,583 | 480,583 | 0 | 100.00% (0.00% diff) | **VERIFIED PERFECT** |

---

## 5. Daman & Diu Administrative Evolution (2019–2023)

| Metric | 2019 | 2020 | 2021 | 2022 | 2023 | Source Representation & Meaning |
|---|---|---|---|---|---|---|
| **Daman & Diu Accidents** | 69 | 67 | 46 | 0 | NULL | 0 in 2022 was an explicit zero reported; NULL in 2023 reflects reporting discontinued and merged under Dadra & Nagar Haveli. |
| **Daman & Diu Fatalities** | 28 | 27 | 17 | NULL | NULL | Fatalities ceased separate reporting after 2021. |
| **Dadra & Nagar Haveli* Accidents** | 68 | 54 | 47 | 196 | 182 | Dramatic jump in 2022 (from 47 to 196) marks the absorption of Daman & Diu into combined UT reporting. |
| **Dadra & Nagar Haveli* Fatalities** | 49 | 36 | 39 | 90 | 74 | Fatalities jumped from 39 to 90 in 2022 reflecting consolidated UT numbers. |

### Audit Rule:
- `0` must never be coerced to `NULL` (it certifies that zero occurrences were recorded).
- `NULL` must never be imputed as `0` (it denotes missing, uncollected, or consolidated administrative reporting).

