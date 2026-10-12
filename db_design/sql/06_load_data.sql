-- =============================================================
-- ROAD INSIGHT — PostgreSQL Database
-- File: 06_load_data.sql
-- Purpose: Data loading via staging → transformation → core tables
-- Run after: 05_insert_reference_data.sql
-- 
-- ARCHITECTURE:
--   Raw CSVs → Python ETL (see 06_etl_loader.py) → stg_* tables
--   → SQL transformations below → core normalized tables
-- =============================================================

SET search_path TO road_insight, public;

-- =============================================================
-- STEP 1: LOAD national_historical_stats FROM stg_* 
--         (RA2019_A1.csv — loaded via Python ETL to staging first)
-- =============================================================

-- This assumes stg_road_hist is populated by 06_etl_loader.py
-- The Python ETL handles Indian comma stripping, type casting, CAGR row removal

-- =============================================================
-- STEP 2: LOAD national_annual_stats FROM RoadNoAcc.csv
-- =============================================================

-- Transformation from staging: parse Indian commas, map % change columns
-- Executed by Python ETL; SQL merge shown here for reference

-- =============================================================
-- STEP 3: LOAD state_annual_stats
--         Merge RoadStateWiseAcc.csv + RoadStatewiseKilled.csv
-- =============================================================

-- After Python ETL populates stg_road_state_acc and stg_road_state_killed:

INSERT INTO state_annual_stats (state_id, year, source_id, accident_count, accident_rank, persons_killed, killed_rank)
SELECT
    s.state_id,
    acc.year,
    acc.source_id,
    acc.accident_count,
    acc.accident_rank,
    kil.persons_killed,
    kil.killed_rank
FROM (
    -- Subquery: unpivoted accident data from staging
    -- Populated by Python ETL
    SELECT state_id, year, source_id, accident_count, accident_rank
    FROM stg_state_acc_long   -- intermediate view created by ETL
) acc
LEFT JOIN (
    SELECT state_id, year, persons_killed, killed_rank
    FROM stg_state_kil_long   -- intermediate view created by ETL
) kil ON acc.state_id = kil.state_id AND acc.year = kil.year
ON CONFLICT (state_id, year) DO UPDATE
    SET accident_count  = EXCLUDED.accident_count,
        accident_rank   = EXCLUDED.accident_rank,
        persons_killed  = EXCLUDED.persons_killed,
        killed_rank     = EXCLUDED.killed_rank;

-- =============================================================
-- STEP 4: LOAD city_accident_stats FROM LargeCities.csv
-- =============================================================

-- After Python ETL runs and unpivots LargeCities.csv:

INSERT INTO city_accident_stats (city_id, year, source_id, accident_count, persons_killed, persons_injured, accident_rank, killed_rank, injured_rank)
SELECT
    c.city_id,
    src.year,
    src.source_id,
    src.accident_count,
    src.persons_killed,
    src.persons_injured,
    src.accident_rank,
    src.killed_rank,
    src.injured_rank
FROM stg_city_acc_long src  -- intermediate long-format view from Python ETL
JOIN cities c ON LOWER(c.city_name) = LOWER(src.city_name_clean)
ON CONFLICT (city_id, year) DO UPDATE
    SET accident_count = EXCLUDED.accident_count,
        persons_killed = EXCLUDED.persons_killed,
        persons_injured = EXCLUDED.persons_injured,
        accident_rank  = EXCLUDED.accident_rank,
        killed_rank    = EXCLUDED.killed_rank,
        injured_rank   = EXCLUDED.injured_rank;

-- =============================================================
-- STEP 5: LOAD city_violation_stats FROM LargeCitiesVio.csv
-- =============================================================

INSERT INTO city_violation_stats (city_id, year, violation_type_id, source_id, accident_count)
SELECT
    c.city_id,
    2023 AS year,  -- assumed year — VERIFY with source report
    vt.violation_type_id,
    src.source_id,
    src.accident_count
FROM stg_city_vio_long src  -- intermediate long-format view
JOIN cities c ON LOWER(c.city_name) = LOWER(src.city_name_clean)
JOIN violation_types vt ON vt.violation_type_name = src.violation_type_name
ON CONFLICT (city_id, year, violation_type_id) DO UPDATE
    SET accident_count = EXCLUDED.accident_count;

-- =============================================================
-- STEP 6: LOAD city_weather_stats FROM RA2019_A45.csv
-- =============================================================

INSERT INTO city_weather_stats (city_id, year, weather_condition_id, source_id,
    accident_count, persons_killed, persons_grievously_injured,
    persons_minor_injured, persons_total_injured)
SELECT
    c.city_id,
    2019 AS year,
    wc.weather_condition_id,
    src.source_id,
    src.accident_count,
    src.persons_killed,
    src.persons_grievously_injured,
    src.persons_minor_injured,
    src.persons_total_injured
FROM stg_city_wea_long src  -- intermediate long-format view
JOIN cities c ON LOWER(c.city_name) = LOWER(src.city_name_clean)
JOIN weather_conditions wc ON wc.weather_condition_name = src.weather_condition_name
ON CONFLICT (city_id, year, weather_condition_id) DO UPDATE
    SET accident_count              = EXCLUDED.accident_count,
        persons_killed              = EXCLUDED.persons_killed,
        persons_grievously_injured  = EXCLUDED.persons_grievously_injured,
        persons_minor_injured       = EXCLUDED.persons_minor_injured,
        persons_total_injured       = EXCLUDED.persons_total_injured;

-- =============================================================
-- STEP 7: LOAD city_road_feature_stats FROM RA2019_A48.csv
-- =============================================================

INSERT INTO city_road_feature_stats (city_id, year, road_feature_id, source_id,
    accident_count, persons_killed, persons_grievously_injured,
    persons_minor_injured, persons_total_injured)
SELECT
    c.city_id,
    2019 AS year,
    rf.road_feature_id,
    src.source_id,
    src.accident_count,
    src.persons_killed,
    src.persons_grievously_injured,
    src.persons_minor_injured,
    src.persons_total_injured
FROM stg_city_rf_long src   -- intermediate long-format view
JOIN cities c ON LOWER(c.city_name) = LOWER(src.city_name_clean)
JOIN road_features rf ON rf.road_feature_name = src.road_feature_name
ON CONFLICT (city_id, year, road_feature_id) DO UPDATE
    SET accident_count              = EXCLUDED.accident_count,
        persons_killed              = EXCLUDED.persons_killed,
        persons_grievously_injured  = EXCLUDED.persons_grievously_injured,
        persons_minor_injured       = EXCLUDED.persons_minor_injured,
        persons_total_injured       = EXCLUDED.persons_total_injured;

-- =============================================================
-- STEP 8: LOAD collision_type_stats FROM RoadTypeColl.csv
-- =============================================================

INSERT INTO collision_type_stats (collision_type_id, year, source_id,
    accident_count, persons_killed, persons_injured)
SELECT
    ct.collision_type_id,
    src.year,
    src.source_id,
    src.accident_count,
    src.persons_killed,
    src.persons_injured
FROM stg_coll_long src   -- intermediate long-format view
JOIN collision_types ct ON ct.collision_type_name = src.collision_type_name
ON CONFLICT (collision_type_id, year) DO UPDATE
    SET accident_count = EXCLUDED.accident_count,
        persons_killed = EXCLUDED.persons_killed,
        persons_injured = EXCLUDED.persons_injured;

-- =============================================================
-- STEP 9: LOAD violation_type_stats FROM RoadTypeViol.csv
-- =============================================================

INSERT INTO violation_type_stats (violation_type_id, year, source_id,
    accident_count, persons_killed, persons_injured)
SELECT
    vt.violation_type_id,
    src.year,
    src.source_id,
    src.accident_count,
    src.persons_killed,
    src.persons_injured
FROM stg_viol_long src   -- intermediate long-format view
JOIN violation_types vt ON vt.violation_type_name = src.violation_type_name
ON CONFLICT (violation_type_id, year) DO UPDATE
    SET accident_count = EXCLUDED.accident_count,
        persons_killed = EXCLUDED.persons_killed,
        persons_injured = EXCLUDED.persons_injured;
