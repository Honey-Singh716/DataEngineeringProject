-- =============================================================
-- ROAD INSIGHT — PostgreSQL Database
-- File: 04_create_indexes.sql
-- Purpose: Create performance indexes for analytical queries
-- Run after: 03_create_constraints.sql
-- Note: Redundant indexes removed per docs/evidence/indexes/redundant_index_analysis.md
-- =============================================================

SET search_path TO road_insight, public;

-- =============================================================
-- INDEX DESIGN RATIONALE
-- =============================================================
-- 1. Primary Keys and UNIQUE constraints are automatically indexed by PostgreSQL.
-- 2. Identical duplicate indexes and single-column indexes on leading prefixes
--    of unique composite keys (e.g., (state_id, year)) are omitted to prevent
--    write amplification and buffer bloat.
-- 3. This file adds only necessary non-redundant indexes for:
--    a. Non-leading Foreign Key columns (joins)
--    b. Secondary-column year filters (e.g. WHERE year = 2023)
--    c. Analytical composite filters and ORDER BY / ranking columns
--    d. Functional expressions (e.g., LOWER(name))
-- =============================================================

-- =============================================================
-- SECTION 1: FOREIGN KEY INDEXES (Non-Leading Prefix Only)
-- =============================================================

-- cities.state_id → states
CREATE INDEX IF NOT EXISTS idx_cities_state_id
    ON cities (state_id);
-- WHY: Queries joining cities with states (e.g., "cities in Karnataka")

-- state_annual_stats.source_id
CREATE INDEX IF NOT EXISTS idx_state_stats_source_id
    ON state_annual_stats (source_id);
-- WHY: Data lineage / audit queries

-- city_violation_stats.violation_type_id (3rd column in composite key)
CREATE INDEX IF NOT EXISTS idx_city_vio_type_id
    ON city_violation_stats (violation_type_id);
-- WHY: "which cities have most overspeeding accidents"

-- city_weather_stats.weather_condition_id (3rd column in composite key)
CREATE INDEX IF NOT EXISTS idx_city_wea_cond_id
    ON city_weather_stats (weather_condition_id);
-- WHY: "accidents in foggy conditions by city"

-- city_road_feature_stats.road_feature_id (3rd column in composite key)
CREATE INDEX IF NOT EXISTS idx_city_rf_feat_id
    ON city_road_feature_stats (road_feature_id);
-- WHY: "How many accidents on curved roads?"

-- NOTE: idx_state_stats_state_id, idx_city_acc_city_id, idx_city_vio_city_id,
--       idx_city_wea_city_id, idx_city_rf_city_id, idx_coll_type_id, idx_viol_type_id
--       are omitted because they are leading prefixes of unique constraints.

-- =============================================================
-- SECTION 2: YEAR FILTER INDEXES (Secondary column in composite keys)
-- =============================================================
-- B-tree composite index on (state_id, year) cannot efficiently scan on year alone.
-- These dedicated year indexes accelerate national and annual cross-sectional queries.

CREATE INDEX IF NOT EXISTS idx_state_stats_year
    ON state_annual_stats (year);

CREATE INDEX IF NOT EXISTS idx_city_acc_year
    ON city_accident_stats (year);

CREATE INDEX IF NOT EXISTS idx_city_vio_year
    ON city_violation_stats (year);

CREATE INDEX IF NOT EXISTS idx_city_wea_year
    ON city_weather_stats (year);

CREATE INDEX IF NOT EXISTS idx_city_rf_year
    ON city_road_feature_stats (year);

CREATE INDEX IF NOT EXISTS idx_coll_year
    ON collision_type_stats (year);

CREATE INDEX IF NOT EXISTS idx_viol_year
    ON violation_type_stats (year);

-- =============================================================
-- SECTION 3: COMPOSITE ANALYTICAL INDEXES
-- =============================================================

-- city_weather_stats: (year, weather_condition_id) for cross-city analysis
CREATE INDEX IF NOT EXISTS idx_city_wea_year_cond
    ON city_weather_stats (year, weather_condition_id);
-- WHY: "All cities, foggy weather, 2019" pattern

-- city_road_feature_stats: (year, road_feature_id)
CREATE INDEX IF NOT EXISTS idx_city_rf_year_feat
    ON city_road_feature_stats (year, road_feature_id);
-- WHY: "All cities, bridge accidents, 2019"

-- =============================================================
-- SECTION 4: MEASURE INDEXES FOR RANKING QUERIES
-- =============================================================

-- accident_count descending — for "top N cities/states" queries
CREATE INDEX IF NOT EXISTS idx_city_acc_accident_count_desc
    ON city_accident_stats (accident_count DESC NULLS LAST);

CREATE INDEX IF NOT EXISTS idx_city_acc_killed_desc
    ON city_accident_stats (persons_killed DESC NULLS LAST);

CREATE INDEX IF NOT EXISTS idx_state_acc_count_desc
    ON state_annual_stats (accident_count DESC NULLS LAST);

CREATE INDEX IF NOT EXISTS idx_state_killed_desc
    ON state_annual_stats (persons_killed DESC NULLS LAST);

-- =============================================================
-- SECTION 5: FUNCTIONAL TEXT SEARCH INDEXES (for LLM/NLP lookups)
-- =============================================================

-- Case-insensitive state name search
CREATE INDEX IF NOT EXISTS idx_states_name_lower
    ON states (LOWER(state_name));

-- Case-insensitive city name search
CREATE INDEX IF NOT EXISTS idx_cities_name_lower
    ON cities (LOWER(city_name));
