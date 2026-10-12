-- =============================================================
-- ROAD INSIGHT — PostgreSQL Database
-- File: 07_validation_queries.sql
-- Purpose: Data quality validation after loading
-- Run after: 06_load_data.sql
-- =============================================================

SET search_path TO road_insight, public;

-- =============================================================
-- SECTION 1: ROW COUNT CHECKS
-- Expected counts after loading
-- =============================================================

-- 1.1 Reference tables
SELECT 'data_sources'       AS table_name, COUNT(*) AS row_count, 10 AS expected FROM data_sources
UNION ALL
SELECT 'states',             COUNT(*), 37 FROM states
UNION ALL
SELECT 'cities',             COUNT(*), 50 FROM cities
UNION ALL
SELECT 'weather_conditions', COUNT(*), 5  FROM weather_conditions
UNION ALL
SELECT 'road_features',      COUNT(*), 8  FROM road_features
UNION ALL
SELECT 'collision_types',    COUNT(*), 9  FROM collision_types
UNION ALL
SELECT 'violation_types',    COUNT(*), 6  FROM violation_types;

-- 1.2 Fact tables
SELECT 'national_historical_stats' AS table_name, COUNT(*) AS row_count, 29 AS expected FROM national_historical_stats
UNION ALL
SELECT 'national_annual_stats',   COUNT(*),  5 FROM national_annual_stats
UNION ALL
SELECT 'state_annual_stats',      COUNT(*), 37*5  FROM state_annual_stats   -- 37 states x 5 years = 185 max (NULLs for missing)
UNION ALL
SELECT 'city_accident_stats',     COUNT(*), 50*2  FROM city_accident_stats  -- 50 cities x 2 years = 100
UNION ALL
SELECT 'city_violation_stats',    COUNT(*), 50*6  FROM city_violation_stats -- 50 cities x 6 violation types = 300
UNION ALL
SELECT 'city_weather_stats',      COUNT(*), 50*5  FROM city_weather_stats   -- 50 cities x 5 weather conditions = 250
UNION ALL
SELECT 'city_road_feature_stats', COUNT(*), 50*8  FROM city_road_feature_stats -- 50 cities x 8 road features = 400
UNION ALL
SELECT 'collision_type_stats',    COUNT(*), 9*2   FROM collision_type_stats -- 9 types x 2 years = 18
UNION ALL
SELECT 'violation_type_stats',    COUNT(*), 6*2   FROM violation_type_stats; -- 6 types x 2 years = 12

-- =============================================================
-- SECTION 2: ORPHAN FOREIGN KEY CHECKS
-- These should return 0 rows. Non-zero = referential integrity failure.
-- =============================================================

-- 2.1 Cities with invalid state_id
SELECT 'cities with invalid state_id' AS check_name, COUNT(*) AS violation_count
FROM cities
WHERE state_id IS NOT NULL
  AND state_id NOT IN (SELECT state_id FROM states);

-- 2.2 state_annual_stats with invalid state_id
SELECT 'state_annual_stats invalid state_id' AS check_name, COUNT(*) AS violation_count
FROM state_annual_stats
WHERE state_id NOT IN (SELECT state_id FROM states);

-- 2.3 city_accident_stats with invalid city_id
SELECT 'city_accident_stats invalid city_id' AS check_name, COUNT(*) AS violation_count
FROM city_accident_stats
WHERE city_id NOT IN (SELECT city_id FROM cities);

-- 2.4 city_violation_stats with invalid violation_type_id
SELECT 'city_violation_stats invalid violation_type_id' AS check_name, COUNT(*) AS violation_count
FROM city_violation_stats
WHERE violation_type_id NOT IN (SELECT violation_type_id FROM violation_types);

-- 2.5 city_weather_stats with invalid weather_condition_id
SELECT 'city_weather_stats invalid weather_condition_id' AS check_name, COUNT(*) AS violation_count
FROM city_weather_stats
WHERE weather_condition_id NOT IN (SELECT weather_condition_id FROM weather_conditions);

-- 2.6 city_road_feature_stats with invalid road_feature_id
SELECT 'city_road_feature_stats invalid road_feature_id' AS check_name, COUNT(*) AS violation_count
FROM city_road_feature_stats
WHERE road_feature_id NOT IN (SELECT road_feature_id FROM road_features);

-- 2.7 collision_type_stats with invalid collision_type_id
SELECT 'collision_type_stats invalid collision_type_id' AS check_name, COUNT(*) AS violation_count
FROM collision_type_stats
WHERE collision_type_id NOT IN (SELECT collision_type_id FROM collision_types);

-- =============================================================
-- SECTION 3: DUPLICATE PRIMARY KEY / UNIQUE KEY CHECKS
-- =============================================================

-- 3.1 Duplicate state names
SELECT state_name, COUNT(*) AS dup_count
FROM states
GROUP BY state_name
HAVING COUNT(*) > 1;

-- 3.2 Duplicate city names
SELECT city_name, COUNT(*) AS dup_count
FROM cities
GROUP BY city_name
HAVING COUNT(*) > 1;

-- 3.3 Duplicate (state_id, year) in state_annual_stats
SELECT state_id, year, COUNT(*) AS dup_count
FROM state_annual_stats
GROUP BY state_id, year
HAVING COUNT(*) > 1;

-- 3.4 Duplicate (city_id, year) in city_accident_stats
SELECT city_id, year, COUNT(*) AS dup_count
FROM city_accident_stats
GROUP BY city_id, year
HAVING COUNT(*) > 1;

-- =============================================================
-- SECTION 4: NULL CHECKS
-- =============================================================

-- 4.1 state_annual_stats with NULL accident_count (legitimate for Ladakh/Daman & Diu)
SELECT s.state_name, sas.year, sas.accident_count
FROM state_annual_stats sas
JOIN states s ON sas.state_id = s.state_id
WHERE sas.accident_count IS NULL
ORDER BY s.state_name, sas.year;
-- EXPECTED: Ladakh 2019-2020, Daman & Diu 2020-2023 possibly

-- 4.2 city_accident_stats with NULL values (should be none)
SELECT city_id, year
FROM city_accident_stats
WHERE accident_count IS NULL
   OR persons_killed IS NULL
   OR persons_injured IS NULL;

-- 4.3 national_historical_stats NULL road_length (expected: 2019)
SELECT year, road_length_km
FROM national_historical_stats
WHERE road_length_km IS NULL;
-- EXPECTED: year = 2019

-- =============================================================
-- SECTION 5: RANGE CHECKS
-- =============================================================

-- 5.1 Negative accident counts (should return 0 rows)
SELECT 'national_annual_stats negative accidents' AS check_name, COUNT(*) AS violations
FROM national_annual_stats WHERE total_accidents < 0
UNION ALL
SELECT 'state_annual_stats negative accident_count', COUNT(*)
FROM state_annual_stats WHERE accident_count < 0
UNION ALL
SELECT 'city_accident_stats negative accident_count', COUNT(*)
FROM city_accident_stats WHERE accident_count < 0
UNION ALL
SELECT 'city_accident_stats negative persons_killed', COUNT(*)
FROM city_accident_stats WHERE persons_killed < 0
UNION ALL
SELECT 'collision_type_stats negative accident_count', COUNT(*)
FROM collision_type_stats WHERE accident_count < 0;

-- 5.2 Year range validation
SELECT 'national_historical_stats out of year range' AS check_name, COUNT(*)
FROM national_historical_stats
WHERE year < 1970 OR year > 2030
UNION ALL
SELECT 'state_annual_stats out of year range', COUNT(*)
FROM state_annual_stats
WHERE year < 2019 OR year > 2030
UNION ALL
SELECT 'city_accident_stats out of year range', COUNT(*)
FROM city_accident_stats
WHERE year < 2019 OR year > 2030;

-- =============================================================
-- SECTION 6: REFERENTIAL INTEGRITY — AGGREGATE CROSS-CHECKS
-- =============================================================

-- 6.1 Sum of state accidents should equal national total for each year
SELECT
    nas.year,
    nas.total_accidents AS national_total,
    SUM(sas.accident_count) AS sum_of_states,
    (nas.total_accidents - SUM(sas.accident_count)) AS difference
FROM national_annual_stats nas
LEFT JOIN state_annual_stats sas ON sas.year = nas.year
GROUP BY nas.year, nas.total_accidents
ORDER BY nas.year;
-- NOTE: Difference may not be zero due to NULLs (Ladakh, Daman & Diu)
-- and because national figures may include UTs not separately reported

-- 6.2 Sum of collision type accidents vs national total (for 2022 and 2023)
SELECT
    nas.year,
    nas.total_accidents AS national_total,
    SUM(cts.accident_count) AS collision_type_sum,
    (nas.total_accidents - SUM(cts.accident_count)) AS difference
FROM national_annual_stats nas
JOIN collision_type_stats cts ON cts.year = nas.year
GROUP BY nas.year, nas.total_accidents
ORDER BY nas.year;

-- 6.3 Killed: total injured >= grievously injured + minor injured check for city_weather_stats
SELECT city_id, year, weather_condition_id,
       persons_total_injured,
       persons_grievously_injured + persons_minor_injured AS computed_total,
       persons_total_injured - (persons_grievously_injured + persons_minor_injured) AS diff
FROM city_weather_stats
WHERE persons_total_injured != persons_grievously_injured + persons_minor_injured
ORDER BY ABS(persons_total_injured - (persons_grievously_injured + persons_minor_injured)) DESC
LIMIT 20;

-- =============================================================
-- SECTION 7: ANALYTICAL SANITY CHECKS
-- These validate that key business queries return sensible results
-- =============================================================

-- 7.1 Top 5 states by accidents in 2023
SELECT s.state_name, sas.accident_count
FROM state_annual_stats sas
JOIN states s ON sas.state_id = s.state_id
WHERE sas.year = 2023
ORDER BY sas.accident_count DESC NULLS LAST
LIMIT 5;
-- EXPECTED: Tamil Nadu, Madhya Pradesh, Uttar Pradesh, Kerala, Karnataka (approx)

-- 7.2 Top 5 cities by fatalities in 2023
SELECT c.city_name, cas.persons_killed
FROM city_accident_stats cas
JOIN cities c ON cas.city_id = c.city_id
WHERE cas.year = 2023
ORDER BY cas.persons_killed DESC
LIMIT 5;
-- EXPECTED: Delhi, Tamil Nadu cities, Rajasthan cities

-- 7.3 National trend in accidents 2019-2023
SELECT year, total_accidents, total_fatalities,
       accidents_pct_change, fatalities_pct_change
FROM national_annual_stats
ORDER BY year;

-- 7.4 Most dangerous road feature (by killed, 2019, all cities)
SELECT rf.road_feature_name,
       SUM(crfs.accident_count) AS total_accidents,
       SUM(crfs.persons_killed) AS total_killed
FROM city_road_feature_stats crfs
JOIN road_features rf ON crfs.road_feature_id = rf.road_feature_id
WHERE crfs.year = 2019
GROUP BY rf.road_feature_name
ORDER BY total_killed DESC;

-- 7.5 Most dangerous weather condition (by accidents, 2019)
SELECT wc.weather_condition_name,
       SUM(cws.accident_count) AS total_accidents,
       SUM(cws.persons_killed) AS total_killed
FROM city_weather_stats cws
JOIN weather_conditions wc ON cws.weather_condition_id = wc.weather_condition_id
WHERE cws.year = 2019
GROUP BY wc.weather_condition_name
ORDER BY total_accidents DESC;

-- 7.6 Leading collision type in 2023
SELECT ct.collision_type_name, cts.accident_count, cts.persons_killed
FROM collision_type_stats cts
JOIN collision_types ct ON cts.collision_type_id = ct.collision_type_id
WHERE cts.year = 2023
ORDER BY cts.accident_count DESC;

-- 7.7 Leading violation type in 2023
SELECT vt.violation_type_name, vts.accident_count
FROM violation_type_stats vts
JOIN violation_types vt ON vts.violation_type_id = vt.violation_type_id
WHERE vts.year = 2023
ORDER BY vts.accident_count DESC;

-- 7.8 Historical trend — accidents per lakh population (1970-2019)
SELECT year, total_accidents, accidents_per_lakh_pop
FROM national_historical_stats
ORDER BY year;

-- =============================================================
-- SECTION 8: SOURCE TRACEABILITY CHECK
-- =============================================================

-- 8.1 Every fact row should have a valid source_id
SELECT 'national_historical_stats missing source' AS check_name, COUNT(*)
FROM national_historical_stats
WHERE source_id NOT IN (SELECT source_id FROM data_sources)
UNION ALL
SELECT 'state_annual_stats missing source', COUNT(*)
FROM state_annual_stats
WHERE source_id NOT IN (SELECT source_id FROM data_sources)
UNION ALL
SELECT 'city_accident_stats missing source', COUNT(*)
FROM city_accident_stats
WHERE source_id NOT IN (SELECT source_id FROM data_sources);

-- 8.2 Show row count per source_id (data provenance summary)
SELECT ds.source_file, ds.geographic_scope,
       (SELECT COUNT(*) FROM state_annual_stats sas WHERE sas.source_id = ds.source_id)  AS state_rows,
       (SELECT COUNT(*) FROM city_accident_stats cas WHERE cas.source_id = ds.source_id) AS city_rows
FROM data_sources ds
ORDER BY ds.source_id;
