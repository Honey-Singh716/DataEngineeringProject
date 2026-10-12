# NORMALIZATION REPORT — ROAD INSIGHT
## AI-Powered Indian Road Accident Analysis System
**Version:** 1.0 | **Date:** 2026-09-21

---

## TABLE: data_sources

**PURPOSE:** Tracks every source CSV file loaded. Enables data provenance and traceability.

**PRIMARY KEY:** `source_id` (SMALLINT IDENTITY) — surrogate key; natural candidate would be source_file but file names could theoretically repeat across versions.

**FOREIGN KEYS:** None (root reference table)

**FUNCTIONAL DEPENDENCIES:**
- source_id → source_file, source_directory, description, report_year, data_year_min, data_year_max, geographic_scope, notes

**1NF:** YES — atomic values, no repeating groups, clear PK.
**2NF:** YES — no composite key; all attributes depend on single PK.
**3NF:** YES — no transitive dependencies between non-key attributes.

**WHY THIS TABLE EXISTS:** Without provenance tracking, no database record can be traced to its origin file. Required for audit, reprocessing, and LLM metadata.

**WHAT WAS REMOVED:** Nothing — this is a new table created for provenance.

---

## TABLE: states

**PURPOSE:** Reference dimension for all 37 Indian States and Union Territories in the source data.

**PRIMARY KEY:** `state_id` (SMALLINT IDENTITY) — surrogate. Natural key `state_name` is also UNIQUE.

**FOREIGN KEYS:** None

**FUNCTIONAL DEPENDENCIES:**
- state_id → state_name, state_type, is_active, notes
- state_name → state_type (states have a defined administrative type)

**1NF:** YES
**2NF:** YES
**3NF:** YES — state_name → state_type is a direct dependency on the key; no transitive path through a non-key attribute.

**WHY THIS TABLE EXISTS:**
- `state_name` appeared in RoadStateWiseAcc.csv and RoadStatewiseKilled.csv.
- Storing state_name in every fact row would violate 3NF (transitive via state_type).
- A separate dimension allows consistent name management and FK enforcement.

**WHAT WAS REMOVED FROM RAW DATA:**
- state_type was not in source — added for completeness.
- Source `"J & K #"` footnote → cleaned to `"Jammu & Kashmir"`.
- Source `"Dadra & Nagar Haveli*"` → standardized to official merged UT name.

---

## TABLE: cities

**PURPOSE:** Reference dimension for 50 large Indian cities tracked in MoRTH city reports.

**PRIMARY KEY:** `city_id` (SMALLINT IDENTITY)

**FOREIGN KEYS:**
- `state_id` → states(state_id) [ON DELETE RESTRICT]

**FUNCTIONAL DEPENDENCIES:**
- city_id → city_name, state_id
- city_name → state_id (a city belongs to one state — deterministic for large cities)

**1NF:** YES
**2NF:** YES
**3NF:** YES — city_name → state_id is a direct dependency; state_name is NOT stored here (would be transitive: city → state_id → state_name).

**WHY THIS TABLE EXISTS:**
- city_name appeared across LargeCities, LargeCitiesVio, RA2019_A45, RA2019_A48.
- Storing city_name repeatedly in fact tables would cause update anomalies.
- State name would also need to be repeated without this dimension.

**WHAT WAS REMOVED:**
- Source city names standardized (Kozhikode, Malappuram, Thiruvananthapuram, Vijayawada, Visakhapatnam).

---

## TABLE: weather_conditions

**PURPOSE:** Reference lookup for weather condition types (5 values).

**PRIMARY KEY:** `weather_condition_id` (SMALLINT IDENTITY)
**UNIQUE:** `weather_condition_name`

**FUNCTIONAL DEPENDENCIES:**
- weather_condition_id → weather_condition_name, description

**1NF:** YES
**2NF:** YES
**3NF:** YES

**WHY THIS TABLE EXISTS:**
- weather_condition_name appeared as column prefix in RA2019_A45.csv (wide format).
- After unpivoting, it becomes a repeating categorical value — normalized into a lookup.
- Prevents misspellings and allows adding descriptions.

---

## TABLE: road_features

**PURPOSE:** Reference lookup for road infrastructure feature types (8 values).

**PRIMARY KEY:** `road_feature_id` (SMALLINT IDENTITY)
**UNIQUE:** `road_feature_name`

**WHY THIS TABLE EXISTS:**
- Same rationale as weather_conditions — column prefixes in RA2019_A48.csv.
- After unpivoting, road_feature_name becomes a repeated categorical value.

**1NF/2NF/3NF:** YES

---

## TABLE: collision_types

**PURPOSE:** Reference lookup for types of road collisions (9 values).

**PRIMARY KEY:** `collision_type_id` (SMALLINT IDENTITY)
**UNIQUE:** `collision_type_name`

**WHY THIS TABLE EXISTS:**
- "Type of collision" in RoadTypeColl.csv is a categorical dimension.
- Normalized to allow FK enforcement and future descriptions/codes.

**1NF/2NF/3NF:** YES

---

## TABLE: violation_types

**PURPOSE:** Reference lookup for traffic violation cause categories (6 values).

**PRIMARY KEY:** `violation_type_id` (SMALLINT IDENTITY)
**UNIQUE:** `violation_type_name`

**WHY THIS TABLE EXISTS:**
- "Category" in RoadTypeViol.csv and the 6 violation columns in LargeCitiesVio.csv represent the same dimension.
- Normalizing avoids duplicating violation type names across two fact tables.
- Enables JOIN between city-level and national-level violation data.

**1NF/2NF/3NF:** YES

---

## TABLE: national_historical_stats

**PURPOSE:** National road accident statistics from 1970 to 2019, including context denominators and derived rates.

**PRIMARY KEY:** `stat_id` (BIGINT IDENTITY)
**UNIQUE:** `year`
**SOURCE:** RA2019_A1.csv

**FUNCTIONAL DEPENDENCIES:**
- stat_id → year (and all other columns)
- year → total_accidents, total_killed, total_injured, population_thousands, ...
- (population_thousands, total_accidents) → accidents_per_lakh_pop [DERIVED]

**1NF:** YES — all values are atomic.
**2NF:** YES — no composite key.
**3NF:** TECHNICALLY PARTIAL — the rate columns (accidents_per_lakh_pop etc.) are functionally determined by base columns (total_accidents, population_thousands) which themselves depend on year. This is a transitive dependency through non-key attributes.

**DESIGN DECISION ON 3NF VIOLATION:**
The rate columns are stored despite being derivable. Reasons:
1. Derived rates were source-provided (RA2019_A1.csv) with higher precision than a simple division.
2. Historical denominators (population, vehicles, road length) are stored here — making rates computable.
3. For a Text-to-SQL/LLM system, direct column access is preferable to requiring the LLM to construct division formulas.
4. The table is historical (1970-2019) and will not be updated — no risk of update anomaly.

**WHAT WAS REMOVED:**
- CAGR (Compound Annual Growth Rate) row — not a year observation.
- Trailing spaces from column names.

**RELATIONSHIPS:**
- data_sources (source_id) 1:N national_historical_stats

---

## TABLE: national_annual_stats

**PURPOSE:** National annual road accident summary for 2019-2023.

**PRIMARY KEY:** `stat_id` (BIGINT IDENTITY)
**UNIQUE:** `year`
**SOURCE:** RoadNoAcc.csv

**FUNCTIONAL DEPENDENCIES:**
- year → total_accidents, total_fatalities, total_injured
- (year, prior year's total_accidents) → accidents_pct_change [DERIVED]

**1NF:** YES
**2NF:** YES
**3NF:** YES for base columns. The pct_change columns are stored for convenience (same justification as national_historical_stats rates).

**WHY SEPARATE FROM national_historical_stats:**
- Different source file, different columns (no population/vehicle/road denominators).
- Overlapping only at year 2019 — both retained for source traceability.

---

## TABLE: state_annual_stats

**PURPOSE:** State/UT level accident and fatality counts for 2019-2023. One row per state × year.

**PRIMARY KEY:** `stat_id` (BIGINT IDENTITY)
**COMPOSITE UNIQUE:** `(state_id, year)`
**SOURCES:** RoadStateWiseAcc.csv + RoadStatewiseKilled.csv (merged)

**FOREIGN KEYS:**
- state_id → states(state_id)
- source_id → data_sources(source_id)

**FUNCTIONAL DEPENDENCIES:**
- (state_id, year) → accident_count, accident_rank, persons_killed, killed_rank

**1NF:** YES — one row per state per year after unpivoting.

**2NF STATUS:**
- The composite (state_id, year) uniquely determines all attributes.
- accident_count depends on BOTH state_id and year — full dependency. YES 2NF.

**3NF STATUS:**
- accident_rank depends on (accident_count, year) across all states — it is derived from cross-state comparison.
- DESIGN DECISION: Rank stored despite being derivable from accident_count (using RANK() OVER). Stored because it was source-supplied and avoids requiring complex window function in every query.
- No transitive dependency through non-key attributes otherwise.

**WHAT WAS REMOVED FROM RAW DATA:**
- `Change from 2022 to 2023` column (=2023-2022, trivially derivable).
- `% change from 2022 to 2023` column (derivable via LAG() window function — see vw_state_yoy_comparison view).
- Two source files merged into one normalized table (eliminated file-level redundancy).

**WHAT WAS ADDED:**
- Source joined on state_name to create state_id FK.
- NULL values correctly assigned for Ladakh 2019-2020, Daman & Diu 2020+.

---

## TABLE: city_accident_stats

**PURPOSE:** City-level accident, fatality, and injury statistics for 50 cities, 2022 and 2023.

**PRIMARY KEY:** `stat_id` (BIGINT IDENTITY)
**COMPOSITE UNIQUE:** `(city_id, year)`
**SOURCE:** LargeCities.csv (unpivoted)

**FUNCTIONAL DEPENDENCIES:**
- (city_id, year) → accident_count, persons_killed, persons_injured, accident_rank, killed_rank, injured_rank

**1NF:** YES — after unpivoting from wide to long format.
**2NF:** YES — all attributes fully depend on (city_id, year).
**3NF:** YES — ranking stored (same justification as state_annual_stats).

**WHAT WAS REMOVED:**
- `Sl No` column (not a stable identifier).
- Wide columns pivoted — now represented by `year` column.

---

## TABLE: city_violation_stats

**PURPOSE:** Accident counts attributed to each traffic violation type, by city, per year.

**PRIMARY KEY:** `stat_id` (BIGINT IDENTITY)
**COMPOSITE UNIQUE:** `(city_id, year, violation_type_id)`
**SOURCE:** LargeCitiesVio.csv (unpivoted)

**FUNCTIONAL DEPENDENCIES:**
- (city_id, year, violation_type_id) → accident_count

**1NF:** YES — after unpivoting the 6 violation columns.
**2NF:** YES — accident_count depends on all three key components.
**3NF:** YES — no non-key attributes besides accident_count.

**WHY NOT ONE ROW PER CITY:**
The raw file had 6 violation columns per city row. Storing them normalized (one row per violation type) allows:
- Querying by violation type across all cities (no case expressions needed)
- Joining with violation_types reference table
- Analytically comparing violation distributions across cities

**WHAT WAS REMOVED:**
- % share rows (not in this file — pre-calculated percentages appear only in national files).

---

## TABLE: city_weather_stats

**PURPOSE:** Accident statistics broken down by weather condition at time of accident, by city, for 2019.

**PRIMARY KEY:** `stat_id` (BIGINT IDENTITY)
**COMPOSITE UNIQUE:** `(city_id, year, weather_condition_id)`
**SOURCE:** RA2019_A45.csv (heavily unpivoted from 28 columns to 5 columns)

**FUNCTIONAL DEPENDENCIES:**
- (city_id, year, weather_condition_id) → accident_count, persons_killed, persons_grievously_injured, persons_minor_injured, persons_total_injured
- persons_total_injured ≈ persons_grievously_injured + persons_minor_injured [NEAR-DERIVED]

**1NF:** YES
**2NF:** YES
**3NF:** DESIGN NOTE: `persons_total_injured` is approximately derivable from grievously + minor. Stored because:
1. Source provided it directly (pre-aggregated).
2. Small discrepancies may exist in source.
3. Eliminates summation in every query.
A CHECK constraint verifies approximate equality in 07_validation_queries.sql.

**WHAT WAS REMOVED:**
- Rank columns (only existed for Sunny/Clear — inconsistent; not stored in normalized table).
- Source typo "Greviously" corrected to "Grievously" in column naming.
- Wide format (28 columns) → long format (8 columns).

---

## TABLE: city_road_feature_stats

**PURPOSE:** Accident statistics by road infrastructure feature type, by city, for 2019.

**PRIMARY KEY:** `stat_id` (BIGINT IDENTITY)
**COMPOSITE UNIQUE:** `(city_id, year, road_feature_id)`
**SOURCE:** RA2019_A48.csv (unpivoted from 43 columns)

**FUNCTIONAL DEPENDENCIES:**
- (city_id, year, road_feature_id) → accident_count, persons_killed, persons_grievously_injured, persons_minor_injured, persons_total_injured

**1NF/2NF/3NF:** YES — same rationale as city_weather_stats.

**WHAT WAS REMOVED:**
- Rank columns (only for Straight Road — inconsistent).
- Double spaces in column names fixed.
- 43 columns unpivoted to 9 columns.

---

## TABLE: collision_type_stats

**PURPOSE:** National accident statistics by type of collision for 2022 and 2023.

**PRIMARY KEY:** `stat_id` (BIGINT IDENTITY)
**COMPOSITE UNIQUE:** `(collision_type_id, year)`
**SOURCE:** RoadTypeColl.csv (data rows only)

**FUNCTIONAL DEPENDENCIES:**
- (collision_type_id, year) → accident_count, persons_killed, persons_injured

**1NF/2NF/3NF:** YES

**WHAT WAS REMOVED:**
- "% share" interleaved rows — computed values, not raw data.
- "Total" row — aggregate.
- %Change columns — derivable from (2023_val - 2022_val) / 2022_val.

---

## TABLE: violation_type_stats

**PURPOSE:** National accident statistics by traffic violation cause for 2022 and 2023.

**PRIMARY KEY:** `stat_id` (BIGINT IDENTITY)
**COMPOSITE UNIQUE:** `(violation_type_id, year)`
**SOURCE:** RoadTypeViol.csv (data rows only)

**FUNCTIONAL DEPENDENCIES:**
- (violation_type_id, year) → accident_count, persons_killed, persons_injured

**1NF/2NF/3NF:** YES

---

## FINAL QUALITY CHECKLIST

| Question | Answer | Notes |
|----------|--------|-------|
| Is every final table in at least 3NF? | YES (with documented exceptions) | national_historical_stats stores derived rates — justified |
| Does every table have a proper primary key? | YES | All IDENTITY surrogate keys |
| Are relationships enforced using FK constraints? | YES | All FKs declared in 03_create_constraints.sql |
| Are partial dependencies eliminated? | YES | Wide tables unpivoted; no composite key partial deps |
| Are transitive dependencies eliminated? | YES | State/city names not stored in fact tables |
| Are repeating groups eliminated? | YES | All wide-format files unpivoted to long format |
| Are multi-valued attributes properly modeled? | YES | weather_conditions, road_features as lookup tables |
| Are many-to-many relationships handled? | YES | city_violation_stats, city_weather_stats act as junction-like tables |
| Is duplicate information minimized? | YES | No redundant columns across tables |
| Can every record be traced to source? | YES | source_id FK in every fact table |
| Is there any data loss? | NO | All transformations logged in DATA_CLEANING_LOG.md |
| Can schema support analytical queries? | YES | Views created for all key analytical patterns |
| Is schema understandable by Text-to-SQL? | YES | schema_metadata.json created with full descriptions |
| Are all assumptions documented? | YES | DATA_AUDIT.md and DATA_DICTIONARY.md |
| Can DB be recreated from SQL scripts? | YES | 01-08 SQL scripts + Python ETL loader |
