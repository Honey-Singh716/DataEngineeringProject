-- =============================================================
-- ROAD INSIGHT — PostgreSQL Database
-- File: 08_views.sql
-- Purpose: Analytical views for dashboard, LLM, and reporting
-- Run after: 06_load_data.sql
-- =============================================================

SET search_path TO road_insight, public;

-- =============================================================
-- VIEW 1: vw_state_stats_full
-- Flattened state × year stats with state names
-- PURPOSE: Primary view for state-level analytical queries
-- REPLACES: state_annual_stats JOIN states
-- =============================================================

CREATE OR REPLACE VIEW vw_state_stats_full AS
SELECT
    s.state_id,
    s.state_name,
    s.state_type,
    sas.year,
    sas.accident_count,
    sas.accident_rank,
    sas.persons_killed,
    sas.killed_rank,
    ds.source_file
FROM state_annual_stats sas
JOIN states s ON sas.state_id = s.state_id
JOIN data_sources ds ON sas.source_id = ds.source_id;

COMMENT ON VIEW vw_state_stats_full IS
    'State and Union Territory road accident statistics by year (2019-2023). '
    'Joins state_annual_stats with states and data_sources. '
    'Use this view for state-level trend analysis and ranking queries. '
    'NULLs in accident_count/persons_killed indicate data not separately reported.';

-- =============================================================
-- VIEW 2: vw_city_stats_full
-- Flattened city × year stats with city and state names
-- PURPOSE: City-level analytical queries
-- =============================================================

CREATE OR REPLACE VIEW vw_city_stats_full AS
SELECT
    c.city_id,
    c.city_name,
    s.state_name,
    cas.year,
    cas.accident_count,
    cas.persons_killed,
    cas.persons_injured,
    cas.accident_rank,
    cas.killed_rank,
    cas.injured_rank,
    ds.source_file
FROM city_accident_stats cas
JOIN cities c ON cas.city_id = c.city_id
LEFT JOIN states s ON c.state_id = s.state_id
JOIN data_sources ds ON cas.source_id = ds.source_id;

COMMENT ON VIEW vw_city_stats_full IS
    'City-level road accident statistics (2022-2023) with state context. '
    'Includes accident counts, fatalities, injuries, and rankings among 50 cities.';

-- =============================================================
-- VIEW 3: vw_city_violation_summary
-- City × violation type summary
-- PURPOSE: Identify primary cause categories by city
-- =============================================================

CREATE OR REPLACE VIEW vw_city_violation_summary AS
SELECT
    c.city_id,
    c.city_name,
    s.state_name,
    cvs.year,
    vt.violation_type_name,
    cvs.accident_count,
    SUM(cvs.accident_count) OVER (
        PARTITION BY cvs.city_id, cvs.year
    ) AS city_total_violations,
    ROUND(
        100.0 * cvs.accident_count /
        NULLIF(SUM(cvs.accident_count) OVER (PARTITION BY cvs.city_id, cvs.year), 0),
        2
    ) AS pct_share
FROM city_violation_stats cvs
JOIN cities c ON cvs.city_id = c.city_id
LEFT JOIN states s ON c.state_id = s.state_id
JOIN violation_types vt ON cvs.violation_type_id = vt.violation_type_id;

COMMENT ON VIEW vw_city_violation_summary IS
    'City-level traffic violation breakdown with percentage share calculated dynamically. '
    'Do NOT store pct_share — computed from normalized data to avoid inconsistency.';

-- =============================================================
-- VIEW 4: vw_national_trends
-- National annual + historical stats in one view
-- PURPOSE: Long-term trend analysis for LLM and dashboards
-- =============================================================

CREATE OR REPLACE VIEW vw_national_trends AS
-- Historical data (1970-2019)
SELECT
    year,
    total_accidents,
    total_killed       AS total_fatalities,
    total_injured,
    population_thousands,
    registered_vehicles_thousands,
    road_length_km,
    accidents_per_lakh_pop,
    killed_per_lakh_pop,
    injured_per_lakh_pop,
    'RA2019_A1.csv'    AS source
FROM national_historical_stats
UNION ALL
-- Recent data (2019-2023), excluding 2019 to avoid exact duplicate
SELECT
    year,
    total_accidents,
    total_fatalities,
    total_injured,
    NULL AS population_thousands,
    NULL AS registered_vehicles_thousands,
    NULL AS road_length_km,
    NULL AS accidents_per_lakh_pop,
    NULL AS killed_per_lakh_pop,
    NULL AS injured_per_lakh_pop,
    'RoadNoAcc.csv'    AS source
FROM national_annual_stats
WHERE year > 2019  -- 2019 already in historical table
ORDER BY year;

COMMENT ON VIEW vw_national_trends IS
    'Combined national road accident trends from 1970 to 2023. '
    'Unifies historical (1970-2019) and recent annual (2019-2023) data. '
    'Note: 2019 appears in historical stats with rates; '
    'years 2020-2023 appear from annual stats without rate columns.';

-- =============================================================
-- VIEW 5: vw_collision_type_summary
-- Collision type × year with computed percentages
-- PURPOSE: Understanding how accident types compare
-- =============================================================

CREATE OR REPLACE VIEW vw_collision_type_summary AS
SELECT
    ct.collision_type_name,
    cts.year,
    cts.accident_count,
    cts.persons_killed,
    cts.persons_injured,
    ROUND(100.0 * cts.accident_count /
        NULLIF(SUM(cts.accident_count) OVER (PARTITION BY cts.year), 0), 2
    ) AS pct_of_total_accidents,
    ROUND(100.0 * cts.persons_killed /
        NULLIF(SUM(cts.persons_killed) OVER (PARTITION BY cts.year), 0), 2
    ) AS pct_of_total_killed
FROM collision_type_stats cts
JOIN collision_types ct ON cts.collision_type_id = ct.collision_type_id
ORDER BY cts.year, cts.accident_count DESC;

COMMENT ON VIEW vw_collision_type_summary IS
    'National accident statistics by collision type with dynamically computed percentage shares. '
    'Covers 2022 and 2023.';

-- =============================================================
-- VIEW 6: vw_violation_type_summary
-- Violation type × year with percentages
-- =============================================================

CREATE OR REPLACE VIEW vw_violation_type_summary AS
SELECT
    vt.violation_type_name,
    vts.year,
    vts.accident_count,
    vts.persons_killed,
    vts.persons_injured,
    ROUND(100.0 * vts.accident_count /
        NULLIF(SUM(vts.accident_count) OVER (PARTITION BY vts.year), 0), 2
    ) AS pct_of_total_accidents
FROM violation_type_stats vts
JOIN violation_types vt ON vts.violation_type_id = vt.violation_type_id
ORDER BY vts.year, vts.accident_count DESC;

COMMENT ON VIEW vw_violation_type_summary IS
    'National accident breakdown by traffic violation cause (2022-2023) '
    'with computed percentage shares. '
    'Note: Over-speeding dominates (~68-72% of all accidents).';

-- =============================================================
-- VIEW 7: vw_city_weather_summary
-- Weather condition analysis across cities (2019)
-- =============================================================

CREATE OR REPLACE VIEW vw_city_weather_summary AS
SELECT
    c.city_name,
    s.state_name,
    wc.weather_condition_name,
    cws.year,
    cws.accident_count,
    cws.persons_killed,
    cws.persons_total_injured,
    ROUND(
        CASE WHEN cws.accident_count > 0
             THEN 100.0 * cws.persons_killed / cws.accident_count
             ELSE 0 END,
        2
    ) AS fatality_rate_pct
FROM city_weather_stats cws
JOIN cities c ON cws.city_id = c.city_id
LEFT JOIN states s ON c.state_id = s.state_id
JOIN weather_conditions wc ON cws.weather_condition_id = wc.weather_condition_id;

COMMENT ON VIEW vw_city_weather_summary IS
    'City-level accidents by weather condition (2019) with computed fatality rate. '
    'Fatality rate = persons_killed / accident_count * 100.';

-- =============================================================
-- VIEW 8: vw_city_road_feature_summary
-- Road feature analysis across cities (2019)
-- =============================================================

CREATE OR REPLACE VIEW vw_city_road_feature_summary AS
SELECT
    c.city_name,
    s.state_name,
    rf.road_feature_name,
    crfs.year,
    crfs.accident_count,
    crfs.persons_killed,
    crfs.persons_total_injured,
    ROUND(
        CASE WHEN crfs.accident_count > 0
             THEN 100.0 * crfs.persons_killed / crfs.accident_count
             ELSE 0 END,
        2
    ) AS fatality_rate_pct
FROM city_road_feature_stats crfs
JOIN cities c ON crfs.city_id = c.city_id
LEFT JOIN states s ON c.state_id = s.state_id
JOIN road_features rf ON crfs.road_feature_id = rf.road_feature_id;

COMMENT ON VIEW vw_city_road_feature_summary IS
    'City-level accidents by road infrastructure feature type (2019) '
    'with computed fatality rate per accident.';

-- =============================================================
-- VIEW 9: vw_state_yoy_comparison
-- Year-over-year comparison for states (2019-2023)
-- =============================================================

CREATE OR REPLACE VIEW vw_state_yoy_comparison AS
SELECT
    s.state_name,
    s.state_type,
    sas.year,
    sas.accident_count,
    LAG(sas.accident_count) OVER (PARTITION BY sas.state_id ORDER BY sas.year) AS prev_year_accidents,
    sas.accident_count - LAG(sas.accident_count) OVER (PARTITION BY sas.state_id ORDER BY sas.year) AS yoy_change,
    ROUND(
        100.0 * (sas.accident_count - LAG(sas.accident_count) OVER (PARTITION BY sas.state_id ORDER BY sas.year)) /
        NULLIF(LAG(sas.accident_count) OVER (PARTITION BY sas.state_id ORDER BY sas.year), 0),
        2
    ) AS yoy_pct_change,
    sas.persons_killed,
    LAG(sas.persons_killed) OVER (PARTITION BY sas.state_id ORDER BY sas.year) AS prev_year_killed
FROM state_annual_stats sas
JOIN states s ON sas.state_id = s.state_id
ORDER BY s.state_name, sas.year;

COMMENT ON VIEW vw_state_yoy_comparison IS
    'State-level year-over-year accident and fatality comparisons (2019-2023). '
    'YoY change and percentage computed dynamically using LAG window function. '
    'NULLs expected for 2019 (no prior year) and for states with missing data.';
