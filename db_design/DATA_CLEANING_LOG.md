# DATA CLEANING LOG — ROAD INSIGHT
## AI-Powered Indian Road Accident Analysis System
**Version:** 1.0 | **Date:** 2026-09-21

Format for each entry:
  RAW VALUE → CLEANED VALUE → REASON

---

## SECTION 1: NUMERIC FORMAT CLEANING

### Indian Comma Notation

Applied to: LargeCities.csv, RoadNoAcc.csv, RoadStateWiseAcc.csv,
            RoadStatewiseKilled.csv, RoadTypeColl.csv, RoadTypeViol.csv

Indian number system uses commas at different positions than Western:
  "1,029"   → 1029    → Remove commas, parse as integer
  "76,752"  → 76752   → Remove commas, parse as integer
  "4,56,959"→ 456959  → Remove all commas, parse as integer (Indian lakh format)
  "1,10,656"→ 110656  → Remove all commas, parse as integer
  "1,58,984"→ 158984  → Remove all commas, parse as integer

Rule: Strip ALL commas from numeric strings before casting to INTEGER/NUMERIC.

---

## SECTION 2: ROW REMOVAL (AGGREGATE / FOOTNOTE / BLANK ROWS)

### LargeCities.csv

RAW: Row with Sl No=blank, City="Total" (row 52)
CLEANED: Row removed
REASON: Aggregate total row — not a city record; would cause invalid FK if loaded

### LargeCitiesVio.csv

RAW: Row with Sl No=blank, City="Total" (row 52)
CLEANED: Row removed
REASON: Aggregate total row

### RoadStateWiseAcc.csv

RAW: Row 39: Sl No="Total", State="All India" — aggregate
CLEANED: Row removed
REASON: National total row — not a state record

RAW: Row 40: "# includes Ladakh for 2019 and 2020" in first cell
CLEANED: Row removed
REASON: Footnote text embedded in data — not a data row

RAW: Row 41: "* Dadra and Nagar Haveli includes Daman and Diu" in first cell
CLEANED: Row removed
REASON: Footnote text embedded in data — not a data row

RAW: Row 42: blank row
CLEANED: Row removed
REASON: Empty row

### RoadStatewiseKilled.csv

Same removals as RoadStateWiseAcc.csv applied identically.

### RoadTypeColl.csv

RAW: Rows with "% share" in Type of collision column (e.g., "% share")
CLEANED: Rows removed
REASON: Percentage share rows are derived values interleaved with data rows; computed from the data rows

RAW: Row with Type of collision="Total"
CLEANED: Row removed
REASON: Aggregate total row

### RoadTypeViol.csv

RAW: Rows with "% share of total" in Category column
CLEANED: Rows removed
REASON: Same as RoadTypeColl.csv — derived values

RAW: Row with Category="All India"
CLEANED: Row removed
REASON: Aggregate total row

### RA2019_A1.csv

RAW: Last row with Years="CAGR 2009/2019"
CLEANED: Row removed
REASON: Computed compound annual growth rate — not a year observation

RAW: Last row (blank)
CLEANED: Row removed
REASON: Empty

### RA2019_A45.csv

RAW: Row with States/UTs="Total" (row 52)
CLEANED: Row removed
REASON: Aggregate total row

### RA2019_A48.csv

RAW: Row with State/UT="Total" (row 52)
CLEANED: Row removed
REASON: Aggregate total row

---

## SECTION 3: NULL / MISSING VALUE HANDLING

### RoadStateWiseAcc.csv — "Ladakh"

RAW: 2019 Accidents = "NA", 2020 Accidents = "NA"
CLEANED: NULL (INTEGER NULL)
REASON: Ladakh was part of J&K until 2019/2020; data not separately reported

### RoadStateWiseAcc.csv — "Daman & Diu"

RAW: 2020 Accidents = blank, 2021 Accidents = blank, 2022 Accidents = "0", 2023 Accidents = blank
CLEANED: 2020=NULL, 2021=NULL, 2022=0, 2023=NULL
REASON: Daman & Diu merged into Dadra & Nagar Haveli (UT) from 2020; data merged or unreported

### RoadStateWiseAcc.csv — Ranking "#N/A"

RAW: 2023 Ranking for "Daman & Diu" = "#N/A"
CLEANED: NULL
REASON: Excel formula error (#N/A) embedded in CSV — no valid rank exists for merged UT

### RoadStateWiseAcc.csv — Ranking "Na"

RAW: 2019 Ranking for "Ladakh" = "Na" and 2020 Ranking = "NA"
CLEANED: NULL
REASON: Not available (Ladakh not independently ranked those years)

### RoadStatewiseKilled.csv — same issues as above

Same rules applied for Ladakh and Daman & Diu.

### RA2019_A1.csv — Road Length 2019

RAW: Road Length for 2019 = "NA" (as float NaN after read)
CLEANED: NULL
REASON: Data not available for 2019; rate columns also NULL for 2019

---

## SECTION 4: COLUMN NAME STANDARDIZATION

### RA2019_A48.csv — Double Spaces

RAW: "Straight Road - Persons  Killed - Number" (2 spaces before Killed)
CLEANED: "Straight Road - Persons Killed - Number"
REASON: Whitespace normalization — double space is a typo

Applied to all columns with "Persons  Killed" (double space).

### RA2019_A1.csv — Trailing Spaces

RAW: "Total Number of Road Accidents (in numbers) " (trailing space)
CLEANED: "Total Number of Road Accidents (in numbers)"
REASON: Strip trailing whitespace from column names

Applied to all columns with trailing spaces.

### RoadNoAcc.csv — Duplicate Column Names

RAW: Three columns named "% Change from previous year"
CLEANED: Renamed as:
  Column 3 → "accidents_pct_change"
  Column 5 → "fatalities_pct_change"
  Column 7 → "injured_pct_change"
REASON: Disambiguate duplicate column names for correct mapping

---

## SECTION 5: SPELLING CORRECTIONS

### RA2019_A45.csv and RA2019_A48.csv

RAW: "Greviously Injured" (in column names)
CLEANED: "Grievously Injured"
REASON: Spelling error in source data; standard English term is "grievously"

This affects the naming of the target columns only; the data values are unchanged.

---

## SECTION 6: CITY NAME STANDARDIZATION

The following city names differ across files and are standardized:

RAW: "Allahabad (Prayagraj)" (LargeCities.csv, LargeCitiesVio.csv)
CLEANED: "Allahabad (Prayagraj)"
NOTE: RA2019_A45, RA2019_A48 use "Allahabad(Prayagraj)" (no space)
RESOLUTION: Standardize to "Allahabad (Prayagraj)" (with space) in all files

RAW: "Khozikode" (LargeCities.csv, LargeCitiesVio.csv, RA2019_A45, RA2019_A48)
NOTE: Correct spelling is "Kozhikode" — this is a source data error
CLEANED: Stored as "Kozhikode" — REQUIRES CONFIRMATION before changing
STATUS: FLAGGED FOR REVIEW — correcting may break data lineage

RAW: "Mallapuram" (all files)
NOTE: Correct spelling is "Malappuram" — possible source error
CLEANED: Stored as "Malappuram" — REQUIRES CONFIRMATION
STATUS: FLAGGED FOR REVIEW

RAW: "Thiruvanthapuram" (LargeCities.csv)
vs "Thiruvanthapuram" (RA2019_A45)
NOTE: Official spelling is "Thiruvananthapuram" — consistent across files but may differ from official
CLEANED: Stored as-is unless official correction confirmed

RAW: "Vizaq" (LargeCities.csv, LargeCitiesVio.csv)
vs "Vizaq" (RA2019_A45, RA2019_A48)
NOTE: Appears to be Visakhapatnam; consistent across files
CLEANED: Stored as "Vizaq" with note — REQUIRES VERIFICATION for canonical name

---

## SECTION 7: STATE NAME STANDARDIZATION

### RoadStateWiseAcc.csv

RAW: "J & K #"
CLEANED: "Jammu & Kashmir"
REASON: "#" is footnote reference; standardize to full official name

RAW: "Andaman & Nicobar Islands"
CLEANED: "Andaman & Nicobar Islands"
REASON: No change needed; name is correct

RAW: "Dadra & Nagar Haveli*"
CLEANED: "Dadra & Nagar Haveli and Daman & Diu"
REASON: "*" is footnote; from 2020 this UT merged with Daman & Diu officially

---

## SECTION 8: DATA TYPE CORRECTIONS

| File | Column | Raw Type | Cleaned Type | Reason |
|------|--------|----------|--------------|--------|
| RoadNoAcc | Accidents | string | INTEGER | Indian comma format |
| RoadNoAcc | Fatalities | string | INTEGER | Indian comma format |
| RoadNoAcc | Persons Injured | string | INTEGER | Indian comma format |
| LargeCities | 2022/2023 Accidents/Killed/Injured | string | INTEGER | Indian comma format |
| RoadTypeColl | 2022/2023 columns | string | INTEGER | Indian comma format |
| RoadTypeViol | 2022/2023 columns | string | INTEGER | Indian comma format |
| RA2019_A1 | Years | string | SMALLINT | Year values need integer type |
| RoadStateWiseAcc | 2019-2023 Accidents | int/string | INTEGER | Some NA values, some valid |

---

## SECTION 9: WIDE-TO-LONG (UNPIVOTING) TRANSFORMATIONS

### LargeCities.csv

RAW (wide):
  City | 2022 Accidents | 2023 Accidents | 2022 Killed | 2023 Killed | ...

CLEANED (long):
  city_name | year | accident_count | persons_killed | persons_injured | accident_rank | killed_rank | injured_rank

REASON: One row per city per year for normalized schema; eliminates partial dependencies on year

### RoadStateWiseAcc.csv + RoadStatewiseKilled.csv

RAW (wide):
  State | 2019 Accidents | 2020 Accidents | 2021 Accidents | 2022 Accidents | 2023 Accidents

CLEANED (long, merged):
  state_name | year | accident_count | accident_rank | persons_killed | killed_rank

REASON: Two files share same states and years; merge on state+year for single normalized fact table

### RA2019_A45.csv

RAW (wide, 28 columns):
  City | Sunny/Clear-Accidents | Sunny/Clear-Killed | ... | Rainy-Accidents | ...

CLEANED (long):
  city_name | year | weather_condition | accident_count | persons_killed | persons_grievously_injured | persons_minor_injured | persons_total_injured

REASON: Weather condition becomes a foreign key dimension; data normalized

### RA2019_A48.csv

RAW (wide, 43 columns):
  City | Straight Road-Accidents | Straight Road-Killed | ... | Curved Road-Accidents | ...

CLEANED (long):
  city_name | year | road_feature | accident_count | persons_killed | persons_grievously_injured | persons_minor_injured | persons_total_injured

REASON: Road feature becomes a foreign key dimension; data normalized

---

## SECTION 10: YEAR ASSIGNMENT FOR FILES WITHOUT YEAR COLUMN

| File | Year Assigned | Basis | Confidence |
|------|--------------|-------|------------|
| LargeCitiesVio.csv | 2023 | Contextual (paired with LargeCities 2023 data) | Medium — REQUIRES VERIFICATION |
| RA2019_A45.csv | 2019 | Filename "RA2019" | High |
| RA2019_A48.csv | 2019 | Filename "RA2019" | High |

---

## SECTION 11: DERIVED COLUMN DECISIONS

The following derived columns appear in source data. Decision on whether to store them:

| Column | Decision | Reason |
|--------|----------|--------|
| % Change year-over-year | STORE in national_annual_stats | Small table; pre-computed for convenience |
| State ranking by year | STORE in state_annual_stats | Analytical convenience; source-supplied |
| City ranking by year | STORE in city_accident_stats | Source-supplied; useful for LLM queries |
| Accident rates (per lakh pop, per 10K vehicles) | STORE in national_historical_stats | Historical rates useful; denominator data present |
| % share of total (collision/violation) | DO NOT STORE | Derived from fact table sums; easily computed |
| Change absolute value (2022→2023) | DO NOT STORE | = simple subtraction; can be computed in query |
