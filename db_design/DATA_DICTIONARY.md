# DATA DICTIONARY — ROAD INSIGHT
## AI-Powered Indian Road Accident Analysis System
**Version:** 1.0 | **Date:** 2026-09-21

---

## OVERVIEW

This data dictionary documents every column from every source dataset, its meaning, transformation rules, mapping to the normalized schema, and any ambiguities.

---

## SOURCE FILE: Data/LargeCities.csv

**Grain:** 1 row = 1 large Indian city; columns contain data for 2022 and 2023.

| Column | Raw Name | Data Type | Nullable | Role | Meaning | Maps To (Normalized) |
|--------|----------|-----------|----------|------|---------|----------------------|
| Sl No | `Sl No` | INTEGER | No (data rows) | Sequence | Sequential number 1-50 | Discarded (not a stable ID) |
| City | `City` | VARCHAR | No | Dimension | Name of the large Indian city | `cities.city_name` |
| 2022 Accidents | `2022 Accidents` | INTEGER (after clean) | No | Measure | Total road accidents in city in 2022 | `city_accident_stats.accident_count` |
| 2023 Accidents | `2023 Accidents` | INTEGER (after clean) | No | Measure | Total road accidents in city in 2023 | `city_accident_stats.accident_count` |
| 2022 Ranking Accidents | `2022 Ranking Accidents` | SMALLINT | No | Derived | Rank of city by accident count in 2022 among 50 cities | `city_accident_stats.accident_rank` |
| 2023 Ranking Accidents | `2023 Ranking Accidents` | SMALLINT | No | Derived | Rank in 2023 | `city_accident_stats.accident_rank` |
| 2022 Killed | `2022 Killed` | INTEGER (after clean) | No | Measure | Total persons killed in city in 2022 | `city_accident_stats.persons_killed` |
| 2023 Killed | `2023 Killed` | INTEGER (after clean) | No | Measure | Total persons killed in 2023 | `city_accident_stats.persons_killed` |
| 2022 Ranking Killed | `2022 Ranking Killed` | SMALLINT | No | Derived | Rank by killed in 2022 | `city_accident_stats.killed_rank` |
| 2023 Ranking Killed | `2023 Ranking Killed` | SMALLINT | No | Derived | Rank by killed in 2023 | `city_accident_stats.killed_rank` |
| 2022 Injured | `2022 Injured` | INTEGER (after clean) | No | Measure | Total persons injured in city in 2022 | `city_accident_stats.persons_injured` |
| 2023 Injured | `2023 Injured` | INTEGER (after clean) | No | Measure | Total persons injured in 2023 | `city_accident_stats.persons_injured` |
| 2022 Ranking Injured | `2022 Ranking Injured` | SMALLINT | No | Derived | Rank by injured in 2022 | `city_accident_stats.injured_rank` |
| 2023 Ranking Injured | `2023 Ranking Injured` | SMALLINT | No | Derived | Rank by injured in 2023 | `city_accident_stats.injured_rank` |

**Special rows:**
- Row 52 (Sl No = blank, City = "Total"): Aggregate total — EXCLUDED from load

---

## SOURCE FILE: Data/LargeCitiesVio.csv

**Grain:** 1 row = 1 large Indian city; columns are traffic violation causes.
**Year:** ASSUMED 2023 — REQUIRES VERIFICATION.

| Column | Raw Name | Data Type | Nullable | Role | Meaning | Maps To (Normalized) |
|--------|----------|-----------|----------|------|---------|----------------------|
| Sl No | `Sl No` | INTEGER | No | Sequence | Same order as LargeCities.csv | Discarded |
| City | `City` | VARCHAR | No | Dimension | City name | `cities.city_name` |
| Overspeeding | `Overspeeding` | INTEGER | No | Measure | Accidents attributed to overspeeding | `city_violation_stats.overspeeding_count` |
| Drunken Driving/Drugs use | `Drunken Driving/Drugs use` | INTEGER | No | Measure | Accidents attributed to drunken driving or drug use | `city_violation_stats.drunk_drug_driving_count` |
| Wrong side driving | `Wrong side driving` | INTEGER | No | Measure | Accidents due to wrong-side driving | `city_violation_stats.wrong_side_count` |
| Jumping red light | `Jumping red light` | INTEGER | No | Measure | Accidents due to red light violation | `city_violation_stats.red_light_count` |
| Using Mobile Phone | `Using Mobile Phone` | INTEGER | No | Measure | Accidents due to mobile phone use while driving | `city_violation_stats.mobile_phone_count` |
| Others | `Others` | INTEGER | No | Measure | Accidents due to other unspecified violations | `city_violation_stats.other_violations_count` |

**Special rows:** Row 52 (City = "Total") — EXCLUDED

---

## SOURCE FILE: Data/RoadNoAcc.csv

**Grain:** 1 row = 1 year (national totals).

| Column | Raw Name | Data Type | Nullable | Role | Meaning | Maps To (Normalized) |
|--------|----------|-----------|----------|------|---------|----------------------|
| Year | `Year` | SMALLINT | No | Dimension/PK | Calendar year | `national_annual_stats.year` |
| Accidents | `Accidents` | INTEGER | No | Measure | Total road accidents in India | `national_annual_stats.total_accidents` |
| % Change Accidents | `% Change from previous year` (col 3) | NUMERIC(6,2) | Yes | Derived | YoY change in accidents | `national_annual_stats.accidents_pct_change` |
| Fatalities | `Fatalities` | INTEGER | No | Measure | Total persons killed in India | `national_annual_stats.total_fatalities` |
| % Change Fatalities | `% Change from previous year` (col 5) | NUMERIC(6,2) | Yes | Derived | YoY change in fatalities | `national_annual_stats.fatalities_pct_change` |
| Persons Injured | `Persons Injured` | INTEGER | No | Measure | Total persons injured in India | `national_annual_stats.total_injured` |
| % Change Injured | `% Change from previous year` (col 7) | NUMERIC(6,2) | Yes | Derived | YoY change in injured | `national_annual_stats.injured_pct_change` |

**Note:** The three `% Change` columns have identical names in the raw file. Pandas renames them automatically. These are derived and stored for analytical convenience.

---

## SOURCE FILE: Data/RoadStateWiseAcc.csv

**Grain:** 1 row = 1 state/UT × accident count per year (after unpivoting: 1 row = 1 state × 1 year).

| Column | Raw Name | Data Type | Nullable | Role | Meaning | Maps To (Normalized) |
|--------|----------|-----------|----------|------|---------|----------------------|
| Sl No | `Sl No` | INTEGER | Sometimes | Sequence | Discarded | Discarded |
| State | `State` | VARCHAR | No | Dimension | State or Union Territory name | `states.state_name` |
| 2019 Accidents | `2019 Accidents` | INTEGER | Yes (Ladakh) | Measure | Accident count for 2019 | `state_annual_stats.accident_count` |
| 2020 Accidents | `2020 Accidents` | INTEGER | Yes | Measure | Accident count for 2020 | `state_annual_stats.accident_count` |
| 2021 Accidents | `2021 Accidents` | INTEGER | Yes | Measure | Accident count for 2021 | `state_annual_stats.accident_count` |
| 2022 Accidents | `2022 Accidents` | INTEGER | Yes | Measure | Accident count for 2022 | `state_annual_stats.accident_count` |
| 2023 Accidents | `2023 Accidents` | INTEGER | Yes | Measure | Accident count for 2023 | `state_annual_stats.accident_count` |
| Change from 2022 to 2023 | `Change from 2022 to 2023` | INTEGER | Yes | DERIVED | = 2023 Accidents - 2022 Accidents | NOT STORED (can be computed) |
| % change from 2022 to 2023 | `% change from 2022 to 2023` | NUMERIC(6,2) | Yes | DERIVED | Percentage change | NOT STORED (can be computed) |
| 2019 Ranking through 2023 Ranking | `20XX Ranking` | SMALLINT | Yes | DERIVED | Rank among states | `state_annual_stats.accident_rank` |

**Special rows:**
- "Total" / "All India" row — EXCLUDED
- Footnote rows (# includes..., * Dadra...) — EXCLUDED
- "Daman & Diu": Missing 2021-2023 data — stored as NULL
- "Ladakh": Missing 2019-2020 data — stored as NULL
- "#N/A" text for Daman & Diu ranking — stored as NULL

---

## SOURCE FILE: Data/RoadStatewiseKilled.csv

**Grain:** 1 row = 1 state/UT × killed count per year.

Identical column structure to RoadStateWiseAcc.csv, replacing accident counts with fatality counts.

| Column | Maps To |
|--------|---------|
| State | `states.state_name` |
| 20XX Killed | `state_annual_stats.persons_killed` |
| % change from 2022 to 2023 | DERIVED — NOT STORED |
| 20XX Ranking | `state_annual_stats.killed_rank` |

---

## SOURCE FILE: Data/RoadTypeColl.csv

**Grain (data rows only):** 1 row = 1 collision type × national counts for 2022 and 2023.
**% share rows:** EXCLUDED (derived values).

| Column | Raw Name | Data Type | Nullable | Role | Meaning | Maps To (Normalized) |
|--------|----------|-----------|----------|------|---------|----------------------|
| Type of collision | `Type of collision` | VARCHAR | No | Dimension | Name of collision type | `collision_types.collision_type_name` |
| 2022 Accidents | `2022-Accidents` | INTEGER | No | Measure | National accident count for type in 2022 | `collision_type_stats.accident_count` |
| 2022 Killed | `2022-Killed` | INTEGER | No | Measure | National killed count for type in 2022 | `collision_type_stats.persons_killed` |
| 2022 Injured | `2022-injured` | INTEGER | No | Measure | National injured count for type in 2022 | `collision_type_stats.persons_injured` |
| 2023 Accidents | `2023-Accidents` | INTEGER | No | Measure | National accident count for type in 2023 | `collision_type_stats.accident_count` |
| 2023 Killed | `2023-Killed` | INTEGER | No | Measure | National killed count for type in 2023 | `collision_type_stats.persons_killed` |
| 2023 Injured | `2023-injured` | INTEGER | No | Measure | National injured count for type in 2023 | `collision_type_stats.persons_injured` |
| % Change Accidents | `%Change-Accidents` | NUMERIC(6,2) | Yes | DERIVED | YoY change | NOT STORED (computable) |
| % Change Killed | `%Change-killed` | NUMERIC(6,2) | Yes | DERIVED | YoY change | NOT STORED |
| % Change Injured | `%Change-Injured` | NUMERIC(6,2) | Yes | DERIVED | YoY change | NOT STORED |

**Collision type values (9):**
1. Hit and Run
2. With parked Vehicle
3. Hit from Back
4. Hit from side
5. Run off Road
6. Fixed object
7. Vehicle overturn
8. Head on collision
9. Others

---

## SOURCE FILE: Data/RoadTypeViol.csv

**Grain (data rows only):** 1 row = 1 violation/cause category × national counts for 2022 and 2023.

| Column | Maps To |
|--------|---------|
| Category | `violation_types.violation_type_name` |
| 2022/2023 Accidents/Killed/Injured | `violation_type_stats` |
| % share rows | EXCLUDED (derived) |
| % Change columns | DERIVED — NOT STORED |

**Violation type values (6):**
1. Over-speeding
2. Drunken driving/consumption of alcohol & drug
3. Driving on wrong side/Lane indiscipline
4. Jumping red light
5. Use of mobile phone
6. Others

---

## SOURCE FILE: DataSets/RA2019_A1.csv

**Grain:** 1 row = 1 year (national historical data).
**Year range:** 1970, 1980, 1990, 1994-2019 (not every year between 1970-1993).

| Column | Raw Name | Data Type | Nullable | Role | Meaning | Maps To (Normalized) |
|--------|----------|-----------|----------|------|---------|----------------------|
| Years | `Years` | SMALLINT | No | Dimension/PK | Calendar year | `national_historical_stats.year` |
| Total Accidents | `Total Number of Road Accidents (in numbers)` | INTEGER | No | Measure | National accident count | `national_historical_stats.total_accidents` |
| Total Killed | `Total Number of Persons Killed (in numbers)` | INTEGER | No | Measure | National fatality count | `national_historical_stats.total_killed` |
| Total Injured | `Total Number of Persons Injured (in numbers)` | INTEGER | No | Measure | National injured count | `national_historical_stats.total_injured` |
| Population | `Population of India (in thousands)` | INTEGER | No | Context | Population in thousands | `national_historical_stats.population_thousands` |
| Vehicles | `Total Number of Registered Motor Vehicles (in thousands)` | NUMERIC | No | Context | Registered vehicles in thousands | `national_historical_stats.registered_vehicles_thousands` |
| Road Length | `Road Length (in kms)` | NUMERIC | Yes (2019=NULL) | Context | Total road length in km | `national_historical_stats.road_length_km` |
| Accidents per Lakh Pop | `Number of Accidents per Lakh Population` | NUMERIC(10,6) | Yes | DERIVED | Rate | `national_historical_stats.accidents_per_lakh_pop` |
| Accidents per 10K Vehicles | `Number of Accidents per Ten Thousand Vehicles` | NUMERIC(10,6) | Yes | DERIVED | Rate | `national_historical_stats.accidents_per_10k_vehicles` |
| Accidents per 10K Km Roads | `Number of Accidents per Ten Thousand Kms of Roads` | NUMERIC(10,6) | Yes (2019=NULL) | DERIVED | Rate | `national_historical_stats.accidents_per_10k_km_roads` |
| Killed per Lakh Pop | `Number of Persons Killed Per Lakh Population` | NUMERIC(10,6) | Yes | DERIVED | Rate | `national_historical_stats.killed_per_lakh_pop` |
| Killed per 10K Vehicles | `Number of Persons Killed Per Ten Thousand Vehicles` | NUMERIC(10,6) | Yes | DERIVED | Rate | `national_historical_stats.killed_per_10k_vehicles` |
| Killed per 10K Km Roads | `Number of Persons Killed per Ten Thousand Kms of Roads` | NUMERIC(10,6) | Yes | DERIVED | Rate | `national_historical_stats.killed_per_10k_km_roads` |
| Injured per Lakh Pop | `Number of Persons Injured per Lakh Population` | NUMERIC(10,6) | Yes | DERIVED | Rate | `national_historical_stats.injured_per_lakh_pop` |
| Injured per 10K Vehicles | `Number of Persons Injured Per Ten Thousand Vehicles` | NUMERIC(10,6) | Yes | DERIVED | Rate | `national_historical_stats.injured_per_10k_vehicles` |
| Injured per 10K Km Roads | `Number of Persons Injured Per Ten Thousand Kms of Roads` | NUMERIC(10,6) | Yes | DERIVED | Rate | `national_historical_stats.injured_per_10k_km_roads` |

**Special rows:**
- Last row "CAGR 2009/2019" — EXCLUDED (computed summary, not a year)

---

## SOURCE FILE: DataSets/RA2019_A45.csv

**Grain:** 1 row = 1 city; columns are (weather condition × metric) combinations.
**Year:** 2019 (inferred from filename RA2019).
**After unpivoting grain:** 1 row = 1 city × 1 weather condition × metric values.

| Column Pattern | Raw Example | Normalized Name | Meaning |
|----------------|-------------|-----------------|---------|
| [Weather] - Total Accidents | `Sunny/Clear - Total Accidents - Number` | `accident_count` | Accidents under that weather |
| [Weather] - Persons Killed | `Sunny/Clear - Persons Killed - Number` | `persons_killed` | Killed under that weather |
| [Weather] - Persons Injured - Greviously Injured | ... | `persons_grievously_injured` | Grievously injured (note: "Greviously" = typo) |
| [Weather] - Persons Injured - Minor Injury | ... | `persons_minor_injured` | Minor injuries |
| [Weather] - Persons Injured - Total Injured | ... | `persons_total_injured` | Total injured |
| [Weather] - ... - Rank | `Sunny/Clear - Total Accidents - Rank` | `accident_rank` | Rank (only for Sunny/Clear) |

**Weather conditions (5):** Sunny/Clear, Rainy, Foggy and Misty, Hail/Sleet, Others

**Maps To (Normalized):**
- `cities.city_name` (from column `States/UTs`)
- `weather_conditions.weather_condition_name`
- `city_weather_stats` (fact table)

**Note on "States/UTs" column:** Despite the name, this file contains CITY-level data (large cities), not states. The column header is misleading — it should be labeled "City".

---

## SOURCE FILE: DataSets/RA2019_A48.csv

**Grain:** 1 row = 1 city; columns are (road feature × metric) combinations.
**Year:** 2019 (inferred from filename RA2019).
**After unpivoting grain:** 1 row = 1 city × 1 road feature type × metric values.

| Column Pattern | Normalized Name | Meaning |
|----------------|-----------------|---------|
| [Feature] - Number of Accidents | `accident_count` | Accidents at that road feature |
| [Feature] - Persons Killed | `persons_killed` | Killed |
| [Feature] - Persons Injured - Greviously Injured | `persons_grievously_injured` | Grievously injured |
| [Feature] - Persons Injured - Minor Injury | `persons_minor_injured` | Minor injured |
| [Feature] - Persons Injured - Total Injured | `persons_total_injured` | Total injured |
| [Feature] - ... - Rank | `accident_rank` | Rank (only for Straight Road) |

**Road feature types (8):** Straight Road, Curved Road, Bridge, Culvert, Pot Holes,
Steep Grade, Ongoing Road Works/Under Construction, Others

**Column Name Issues:**
- "Persons  Killed" (double space) — clean to "Persons Killed"
- "Greviously" — standardized to "Grievously"

**Maps To (Normalized):**
- `cities.city_name` (from `State/UT` column — same misleading header)
- `road_features.road_feature_name`
- `city_road_feature_stats` (fact table)

---

## AMBIGUOUS / UNCERTAIN COLUMNS

| Column | File | Ambiguity | Resolution |
|--------|------|-----------|------------|
| Year for LargeCitiesVio.csv | LargeCitiesVio | No year column present | ASSUMED 2023 — REQUIRES VERIFICATION |
| "Vizaq" | LargeCities | Short form; could be Visakhapatnam or Vizianagaram | REQUIRES VERIFICATION — mapped as-is |
| "States/UTs" column header | RA2019_A45, RA2019_A48 | Contains city names, not state names | Documented; treated as City column |
| "Others" violation category | LargeCitiesVio | Does not specify what "Others" includes | Stored as-is; definition unclear |
| "Others" collision type | RoadTypeColl | Does not specify | Stored as-is |
| "Others" weather condition | RA2019_A45 | Does not specify | Stored as-is |
| "Others" road feature | RA2019_A48 | Does not specify | Stored as-is |
| Daman & Diu post-merger | RoadStateWiseAcc, RoadStatewiseKilled | Merged into Dadra & Nagar Haveli — data availability unclear | Stored with NULLs for missing years |
| "J & K #" footnote | RoadStateWiseAcc | "#" indicates includes Ladakh for 2019-2020 | Footnote preserved in `data_sources` |
