-- =============================================================
-- ROAD INSIGHT — PostgreSQL Database
-- File: 04_create_indexes.sql
-- Purpose: Create performance indexes for analytical queries
-- Run after: 03_create_constraints.sql
-- =============================================================

SET search_path TO road_insight, public;

-- =============================================================
-- INDEX DESIGN RATIONALE
-- =============================================================
-- Primary Keys are automatically indexed by PostgreSQL.
-- UNIQUE constraints are automatically indexed.
-- This file adds additional indexes for:
--   1. Foreign key columns (to avoid sequential scans on JOINs)
--   2. Frequently filtered columns (year, state, city)
--   3. Frequently aggregated measure columns
-- =============================================================

-- =============================================================
-- SECTION 1: FOREIGN KEY INDEXES
-- (PostgreSQL does NOT auto-index FK columns)
-- =============================================================

-- cities.state_id → states
CREATE INDEX IF NOT EXISTS idx_cities_state_id
    ON cities (state_id);
-- WHY: Queries joining cities with states (e.g., "cities in Karnataka")

-- state_annual_stats.state_id
CREATE INDEX IF NOT EXISTS idx_state_stats_state_id
    ON state_annual_stats (state_id);
-- WHY: Most state queries filter by state_id

-- state_annual_stats.source_id
CREATE INDEX IF NOT EXISTS idx_state_stats_source_id
    ON state_annual_stats (source_id);
-- WHY: Data lineage / audit queries

-- city_accident_stats.city_id
CREATE INDEX IF NOT EXISTS idx_city_acc_city_id
    ON city_accident_stats (city_id);

-- city_violation_stats.city_id
CREATE INDEX IF NOT EXISTS idx_city_vio_city_id
    ON city_violation_stats (city_id);

-- city_violation_stats.violation_type_id
CREATE INDEX IF NOT EXISTS idx_city_vio_type_id
    ON city_violation_stats (violation_type_id);
-- WHY: Queries like "which cities have most overspeeding accidents"

-- city_weather_stats.city_id
CREATE INDEX IF NOT EXISTS idx_city_wea_city_id
    ON city_weather_stats (city_id);

-- city_weather_stats.weather_condition_id
CREATE INDEX IF NOT EXISTS idx_city_wea_cond_id
    ON city_weather_stats (weather_condition_id);
-- WHY: Queries like "accidents in foggy conditions by city"

-- city_road_feature_stats.city_id
CREATE INDEX IF NOT EXISTS idx_city_rf_city_id
    ON city_road_feature_stats (city_id);

-- city_road_feature_stats.road_feature_id
CREATE INDEX IF NOT EXISTS idx_city_rf_feat_id
    ON city_road_feature_stats (road_feature_id);
-- WHY: "How many accidents on curved roads?"

-- collision_type_stats.collision_type_id
CREATE INDEX IF NOT EXISTS idx_coll_type_id
    ON collision_type_stats (collision_type_id);

-- violation_type_stats.violation_type_id
CREATE INDEX IF NOT EXISTS idx_viol_type_id
    ON violation_type_stats (violation_type_id);

-- =============================================================
-- SECTION 2: YEAR INDEXES
-- Year is the most common filter in analytical queries
-- =============================================================

CREATE INDEX IF NOT EXISTS idx_nat_hist_year
    ON national_historical_stats (year);
-- WHY: Historical trend queries filter by year or year range

CREATE INDEX IF NOT EXISTS idx_nat_ann_year
    ON national_annual_stats (year);

CREATE INDEX IF NOT EXISTS idx_state_stats_year
    ON state_annual_stats (year);
-- WHY: "Accidents in 2023 by state"

CREATE INDEX IF NOT EXISTS idx_city_acc_year
    ON city_accident_stats (year);
-- WHY: "City rankings in 2023"

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
-- SECTION 3: COMPOSITE INDEXES
-- For common multi-column filter patterns
-- =============================================================

-- state_annual_stats: (state_id, year) — most common analytical grain
CREATE INDEX IF NOT EXISTS idx_state_stats_state_year
    ON state_annual_stats (state_id, year);
-- WHY: Covers queries: "State X accident counts by year"
-- ALSO covers: "All states in year Y" (partial index use)

-- city_accident_stats: (city_id, year) — most common city grain
CREATE INDEX IF NOT EXISTS idx_city_acc_city_year
    ON city_accident_stats (city_id, year);

-- city_violation_stats: (city_id, year, violation_type_id)
CREATE INDEX IF NOT EXISTS idx_city_vio_city_year_type
    ON city_violation_stats (city_id, year, violation_type_id);
-- WHY: Covers the natural composite key

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
-- WHY: "Top 10 cities by accidents"

CREATE INDEX IF NOT EXISTS idx_city_acc_killed_desc
    ON city_accident_stats (persons_killed DESC NULLS LAST);
-- WHY: "Top 10 cities by fatalities"

CREATE INDEX IF NOT EXISTS idx_state_acc_count_desc
    ON state_annual_stats (accident_count DESC NULLS LAST);
-- WHY: "State with highest accidents"

CREATE INDEX IF NOT EXISTS idx_state_killed_desc
    ON state_annual_stats (persons_killed DESC NULLS LAST);
-- WHY: "State with highest fatalities"

-- =============================================================
-- SECTION 5: TEXT SEARCH INDEXES (for LLM/NLP lookups)
-- =============================================================

-- Case-insensitive state name search
CREATE INDEX IF NOT EXISTS idx_states_name_lower
    ON states (LOWER(state_name));
-- WHY: Text-to-SQL may generate WHERE LOWER(state_name) = '...' queries

-- Case-insensitive city name search
CREATE INDEX IF NOT EXISTS idx_cities_name_lower
    ON cities (LOWER(city_name));
-- WHY: LLM may produce lowercase or uppercase city name filters
