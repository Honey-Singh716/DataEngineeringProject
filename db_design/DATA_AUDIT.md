# DATA AUDIT — ROAD INSIGHT
## AI-Powered Indian Road Accident Analysis System
**Audit Date:** 2026-09-21  
**Auditor:** Automated + Senior Data Engineer Review

---

## FILES INSPECTED

| # | File | Location | Rows (raw) | Cols | Type |
|---|------|----------|-----------|------|------|
| 1 | `LargeCities.csv` | Data/ | 52 (50 cities + 1 total + 1 blank) | 14 | Fact/Aggregate |
| 2 | `LargeCitiesVio.csv` | Data/ | 52 (50 cities + 1 total + 1 blank) | 7 | Fact/Aggregate |
| 3 | `RoadNoAcc.csv` | Data/ | 6 (5 years + 1 blank) | 7 | National Aggregate |
| 4 | `RoadStateWiseAcc.csv` | Data/ | 41 (37 states + total + 2 footnote + 1 blank) | 13 | State-level Fact |
| 5 | `RoadStatewiseKilled.csv` | Data/ | 41 (37 states + total + 2 footnote + 1 blank) | 12 | State-level Fact |
| 6 | `RoadTypeColl.csv` | Data/ | 20 (9 types + 9 pct_share rows + total + blank) | 10 | Collision Type Aggregate |
| 7 | `RoadTypeViol.csv` | Data/ | 14 (6 categories + 6 pct_share + All India + blank) | 10 | Violation Type Aggregate |
| 8 | `RA2019_A1.csv` | DataSets/ | 31 (29 years + CAGR row + blank) | 16 | Historical National |
| 9 | `RA2019_A45.csv` | DataSets/ | 52 (50 cities + total + blank) | 28 | Weather x City Fact |
| 10 | `RA2019_A48.csv` | DataSets/ | 52 (50 cities + total + blank) | 43 | Road Feature x City Fact |
| 11 | `DE (1).xlsx` | root/ | N/A | N/A | PROJECT MANAGEMENT — NOT DATA |
| 12 | `DE.xlsx` | root/ | Not accessible (OneDrive sync issue) | N/A | UNKNOWN / NEEDS VERIFICATION |

NOTE: DE (1).xlsx contains project planning sheets (Essence Card, Requirements, Sprint Plans, Budget, Traceability Matrix, Test Sheet).
It is NOT a data source and is excluded from database design.
DE.xlsx could not be opened — it may be cloud-only or corrupt. REQUIRES VERIFICATION.

---

## FILE-BY-FILE AUDIT

### 1. Data/LargeCities.csv

Rows (data): 50 cities
Cols: 14
Years: 2022, 2023
Geography: City-level (50 large Indian cities)
Grain: 1 row = 1 city, 2 years combined
File Type: Fact/Aggregate — city-level accident statistics

COLUMNS:
- Sl No          | int    | Sequence ID (NOT a reliable PK)
- City           | string | Dimension (50 cities)
- 2022 Accidents | string | Measure (Indian comma format)
- 2023 Accidents | string | Measure
- 2022 Ranking Accidents | int | Derived/Rank
- 2023 Ranking Accidents | int | Derived/Rank
- 2022 Killed    | string | Measure
- 2023 Killed    | string | Measure
- 2022 Ranking Killed | int | Derived/Rank
- 2023 Ranking Killed | int | Derived/Rank
- 2022 Injured   | string | Measure
- 2023 Injured   | string | Measure
- 2022 Ranking Injured | int | Derived/Rank
- 2023 Ranking Injured | int | Derived/Rank

ISSUES:
- Row 52 is "Total" aggregate row — must be removed
- Numbers in Indian comma notation: "1,029", "76,752" — needs parsing
- Wide format (year pivoted) — needs unpivoting to long format
- Ranking columns are derived — can be recalculated
- City name "Allahabad (Prayagraj)" differs from RA2019_A45 "Allahabad(Prayagraj)" (space)
- "Vizaq" — likely shortform for Visakhapatnam — REQUIRES VERIFICATION

---

### 2. Data/LargeCitiesVio.csv

Rows (data): 50 cities
Cols: 7
Year: 2023 (INFERRED — no year column) — REQUIRES VERIFICATION
Geography: City-level (same 50 cities)
File Type: Fact/Aggregate — traffic violation causes by city

COLUMNS:
- Sl No                     | int    | Sequence
- City                      | string | Dimension
- Overspeeding              | int    | Measure
- Drunken Driving/Drugs use | string | Measure (compound name — one measurement)
- Wrong side driving        | int    | Measure
- Jumping red light         | int    | Measure
- Using Mobile Phone        | int    | Measure
- Others                    | int    | Measure

ISSUES:
- CRITICAL: No year column. Year inferred as 2023 from context — REQUIRES VERIFICATION
- Row 52 is "Total" — remove
- Some cities have 0 in all named categories — possible legitimate data

---

### 3. Data/RoadNoAcc.csv

Rows (data): 5 years (2019-2023)
Cols: 7 (3 duplicate-named columns)
Years: 2019, 2020, 2021, 2022, 2023
Geography: National
File Type: National Annual Aggregate

COLUMNS:
- Year                        | int   | Dimension (PK candidate)
- Accidents                   | string | Measure (Indian comma format)
- % Change from previous year | float | Derived (3 columns share this name — ambiguous)
- Fatalities                  | string | Measure
- % Change from previous year | float | Derived
- Persons Injured             | string | Measure
- % Change from previous year | float | Derived

ISSUES:
- Three columns named "% Change from previous year" — pandas auto-renames
- Numbers in Indian comma format: "4,56,959"
- % Change columns are derived

---

### 4. Data/RoadStateWiseAcc.csv

Rows (data): 37 states/UTs
Cols: 13
Years: 2019-2023
Geography: State/UT level
File Type: State-level Fact

COLUMNS:
- Sl No                    | mixed  | Sequence (rows 39-41 are totals/footnotes)
- State                    | string | Dimension
- 2019-2023 Accidents      | int    | Measure per year
- Change from 2022 to 2023 | int    | Derived = 2023-2022
- % change from 2022 to 2023 | float | Derived
- 2019-2023 Ranking        | int/string | Derived/Rank

ISSUES:
- Row 39 "Total" is aggregate — remove
- Rows 40-41 contain footnote text — remove
- "Daman & Diu": 2021/2022/2023 Accidents are BLANK (merged into Dadra & Nagar Haveli)
- "Ladakh": 2019 and 2020 are "NA" (listed under J&K those years)
- 2023 Ranking for "Daman & Diu" = "#N/A" — corrupt value
- Wide format — needs unpivoting
- "Change from 2022 to 2023" is DERIVED

---

### 5. Data/RoadStatewiseKilled.csv

Rows (data): 37 states/UTs
Cols: 12
Years: 2019-2023
Geography: State/UT level
File Type: State-level Fact

Structure: Identical to RoadStateWiseAcc.csv but for "persons killed" metric.
Same states, same years, same structural issues.

ISSUES:
- "Daman & Diu" row: Only 2019 Killed = 28; all other years blank
- "Haryana" 2020 Killed: "4507" (no comma) vs "4,507" expected — minor inconsistency
- Same footnote/total rows as RoadStateWiseAcc.csv

---

### 6. Data/RoadTypeColl.csv

Rows (data): 9 collision types
Cols: 10
Years: 2022, 2023
Geography: National
File Type: Lookup + Aggregate

COLUMNS:
- Type of collision | string | Dimension (alternating: data row, then "% share" row)
- 2022-Accidents, 2022-Killed, 2022-injured | string | Measure
- 2023-Accidents, 2023-Killed, 2023-injured | string | Measure
- %Change-Accidents, %Change-killed, %Change-Injured | float | Derived

Collision types: Hit and Run, With parked Vehicle, Hit from Back, Hit from side,
Run off Road, Fixed object, Vehicle overturn, Head on collision, Others

ISSUES:
- CRITICAL: Rows alternate between data and "% share" rows — must separate
- Numbers in Indian comma format including "1,10,656" (six-digit with Indian grouping)
- % share rows are derived — exclude from normalized tables
- Total row at bottom — exclude

---

### 7. Data/RoadTypeViol.csv

Rows (data): 6 violation/cause categories
Cols: 10
Years: 2022, 2023
Geography: National
File Type: Lookup + Aggregate

Same structural issue as RoadTypeColl.csv: alternating data + "% share of total" rows.

Violation categories: Over-speeding, Drunken driving/consumption of alcohol & drug,
Driving on wrong side/Lane indiscipline, Jumping red light,
Use of mobile phone, Others

---

### 8. DataSets/RA2019_A1.csv

Rows (data): 29 year-observations (1970-2019, not every year) + 1 CAGR row
Cols: 16
Years: 1970, 1980, 1990, 1994-2019
Geography: National
File Type: Historical National Time Series

COLUMNS (all float except Years):
- Years                                              | string | Dimension
- Total Number of Road Accidents                     | float  | Measure
- Total Number of Persons Killed                     | float  | Measure
- Total Number of Persons Injured                    | float  | Measure
- Population of India (in thousands)                 | float  | Context/Denominator
- Total Number of Registered Motor Vehicles (in thousands) | float | Context/Denominator
- Road Length (in kms)                               | float  | Context/Denominator (NULL for 2019)
- Number of Accidents per Lakh Population            | float  | DERIVED
- Number of Accidents per Ten Thousand Vehicles      | float  | DERIVED
- Number of Accidents per Ten Thousand Kms of Roads  | float  | DERIVED (NULL 2019)
- Number of Persons Killed Per Lakh Population       | float  | DERIVED
- Number of Persons Killed Per Ten Thousand Vehicles | float  | DERIVED
- Number of Persons Killed per Ten Thousand Kms      | float  | DERIVED (NULL 2019)
- Number of Persons Injured per Lakh Population      | float  | DERIVED
- Number of Persons Injured Per Ten Thousand Vehicles| float  | DERIVED
- Number of Persons Injured Per Ten Thousand Kms     | float  | DERIVED (NULL 2019)

ISSUES:
- Last row "CAGR 2009/2019" is a summary row — NOT a year — remove
- Road Length and road-derived rates NULL for 2019
- All rate columns are DERIVED — decision: store for historical reference

---

### 9. DataSets/RA2019_A45.csv

Rows (data): 50 cities
Cols: 28
Year: 2019 (INFERRED from filename)
Geography: City-level (same 50 cities)
File Type: Weather x City Fact — wide format, needs unpivoting

Weather conditions: Sunny/Clear, Rainy, Foggy and Misty, Hail/Sleet, Others
Metrics per condition: Total Accidents, Persons Killed, Grievously Injured, Minor Injured, Total Injured
Rank columns: Only for Sunny/Clear

ISSUES:
- CRITICAL: Heavily pivoted — 5 conditions x 5 metrics = 25 columns
- Rank columns only for Sunny/Clear — inconsistent
- Spelling: "Greviously" should be "Grievously" (source typo)
- Total row at row 52 — remove
- Year NOT in file — inferred as 2019

---

### 10. DataSets/RA2019_A48.csv

Rows (data): 50 cities
Cols: 43
Year: 2019 (INFERRED from filename)
Geography: City-level (same 50 cities)
File Type: Road Feature x City Fact — wide format, needs unpivoting

Road feature types: Straight Road, Curved Road, Bridge, Culvert, Pot Holes,
Steep Grade, Ongoing Road Works/Under Construction, Others
Metrics per feature: Accidents, Killed, Grievously Injured, Minor Injured, Total Injured
Rank columns: Only for Straight Road

ISSUES:
- Double space in column names: "Persons  Killed" (source typo) — trim
- Spelling: "Greviously" (same typo as A45)
- Total row at row 52 — remove
- Year NOT in file — infer as 2019

---

## CROSS-FILE RELATIONSHIPS

| Relationship | Files | Key | Status |
|-------------|-------|-----|--------|
| Same 50 cities | LargeCities, LargeCitiesVio, RA2019_A45, RA2019_A48 | City name | Confirmed |
| Same states | RoadStateWiseAcc, RoadStatewiseKilled | State name | Confirmed |
| Same years 2019-2023 | RoadStateWiseAcc, RoadStatewiseKilled, RoadNoAcc | Year | Confirmed |
| National totals match | RoadNoAcc vs RoadStateWiseAcc total row | Count totals | Confirmed |
| City name spacing diff | LargeCities "Allahabad (Prayagraj)" vs RA2019_A45 "Allahabad(Prayagraj)" | City name | Needs cleaning |
| RA2019 vs 2022/2023 | RA2019_A45, RA2019_A48 vs LargeCities | City+Year | Different years |

---

## DATA QUALITY SUMMARY

| Issue | Severity | Files Affected |
|-------|----------|---------------|
| Indian number format (commas) | High | LargeCities, RoadNoAcc, RoadStateWiseAcc, RoadStatewiseKilled, RoadTypeColl, RoadTypeViol |
| Aggregate/total rows embedded | High | All files |
| Wide/pivoted format | High | LargeCities, RoadStateWiseAcc, RoadStatewiseKilled, RA2019_A45, RA2019_A48 |
| Alternating data + pct rows | High | RoadTypeColl, RoadTypeViol |
| Missing year column | Medium | LargeCitiesVio, RA2019_A45, RA2019_A48 |
| NA/Blank for missing states | Medium | RoadStateWiseAcc, RoadStatewiseKilled |
| Inconsistent city names | Low | LargeCities vs RA2019_A45 |
| Spelling typo "Greviously" | Low | RA2019_A45, RA2019_A48 |
| Footnote rows embedded | Medium | RoadStateWiseAcc, RoadStatewiseKilled |
| Derived columns mixed with raw | Medium | RA2019_A1, RoadStateWiseAcc, RoadTypeColl |
| Double spaces in column names | Low | RA2019_A48 |
| #N/A text values | Medium | RoadStateWiseAcc |
| CAGR row embedded | Medium | RA2019_A1 |
