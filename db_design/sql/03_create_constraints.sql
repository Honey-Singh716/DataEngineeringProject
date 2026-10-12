-- =============================================================
-- ROAD INSIGHT — PostgreSQL Database
-- File: 03_create_constraints.sql
-- Purpose: Add all FK, UNIQUE, CHECK, and DEFAULT constraints
-- Run after: 02_create_tables.sql
-- =============================================================

SET search_path TO road_insight, public;

-- =============================================================
-- SECTION 1: PRIMARY KEY CONSTRAINTS (already declared in CREATE TABLE)
-- Listed here for documentation completeness.
-- =============================================================

-- data_sources.source_id                    PK (IDENTITY)
-- states.state_id                           PK (IDENTITY)
-- cities.city_id                            PK (IDENTITY)
-- weather_conditions.weather_condition_id   PK (IDENTITY)
-- road_features.road_feature_id             PK (IDENTITY)
-- collision_types.collision_type_id         PK (IDENTITY)
-- violation_types.violation_type_id         PK (IDENTITY)
-- national_historical_stats.stat_id         PK (IDENTITY)
-- national_annual_stats.stat_id             PK (IDENTITY)
-- state_annual_stats.stat_id                PK (IDENTITY)
-- city_accident_stats.stat_id               PK (IDENTITY)
-- city_violation_stats.stat_id              PK (IDENTITY)
-- city_weather_stats.stat_id                PK (IDENTITY)
-- city_road_feature_stats.stat_id           PK (IDENTITY)
-- collision_type_stats.stat_id              PK (IDENTITY)
-- violation_type_stats.stat_id              PK (IDENTITY)

-- =============================================================
-- SECTION 2: UNIQUE CONSTRAINTS
-- =============================================================

-- States: state_name must be unique
ALTER TABLE states
    ADD CONSTRAINT uq_states_name UNIQUE (state_name);

-- Cities: city_name must be unique
ALTER TABLE cities
    ADD CONSTRAINT uq_cities_name UNIQUE (city_name);

-- Weather conditions: name already UNIQUE in CREATE TABLE
-- Road features: name already UNIQUE in CREATE TABLE
-- Collision types: name already UNIQUE in CREATE TABLE
-- Violation types: name already UNIQUE in CREATE TABLE

-- National historical stats: one row per year
ALTER TABLE national_historical_stats
    ADD CONSTRAINT uq_nat_hist_year UNIQUE (year);

-- National annual stats: one row per year
ALTER TABLE national_annual_stats
    ADD CONSTRAINT uq_nat_ann_year UNIQUE (year);

-- State annual stats: one row per state per year
ALTER TABLE state_annual_stats
    ADD CONSTRAINT uq_state_year UNIQUE (state_id, year);

-- City accident stats: one row per city per year
ALTER TABLE city_accident_stats
    ADD CONSTRAINT uq_city_acc_year UNIQUE (city_id, year);

-- City violation stats: one row per city × year × violation type
ALTER TABLE city_violation_stats
    ADD CONSTRAINT uq_city_vio_year_type UNIQUE (city_id, year, violation_type_id);

-- City weather stats: one row per city × year × weather condition
ALTER TABLE city_weather_stats
    ADD CONSTRAINT uq_city_weather UNIQUE (city_id, year, weather_condition_id);

-- City road feature stats: one row per city × year × road feature
ALTER TABLE city_road_feature_stats
    ADD CONSTRAINT uq_city_road_feat UNIQUE (city_id, year, road_feature_id);

-- Collision type stats: one row per collision type per year
ALTER TABLE collision_type_stats
    ADD CONSTRAINT uq_coll_type_year UNIQUE (collision_type_id, year);

-- Violation type stats: one row per violation type per year
ALTER TABLE violation_type_stats
    ADD CONSTRAINT uq_viol_type_year UNIQUE (violation_type_id, year);

-- =============================================================
-- SECTION 3: FOREIGN KEY CONSTRAINTS
-- =============================================================
-- Naming convention: fk_{child_table}_{parent_table}

-- ---- cities → states ----
-- A city belongs to a state.
-- ON DELETE RESTRICT: Do not allow deleting a state if cities reference it.
-- ON UPDATE CASCADE: If a state_id changes (not expected), cascade to city.
ALTER TABLE cities
    ADD CONSTRAINT fk_cities_states
    FOREIGN KEY (state_id)
    REFERENCES states (state_id)
    ON DELETE RESTRICT
    ON UPDATE CASCADE;

-- ---- national_historical_stats → data_sources ----
ALTER TABLE national_historical_stats
    ADD CONSTRAINT fk_nat_hist_source
    FOREIGN KEY (source_id)
    REFERENCES data_sources (source_id)
    ON DELETE RESTRICT
    ON UPDATE CASCADE;

-- ---- national_annual_stats → data_sources ----
ALTER TABLE national_annual_stats
    ADD CONSTRAINT fk_nat_ann_source
    FOREIGN KEY (source_id)
    REFERENCES data_sources (source_id)
    ON DELETE RESTRICT
    ON UPDATE CASCADE;

-- ---- state_annual_stats → states ----
-- A state stat row must reference an existing state.
-- ON DELETE RESTRICT: Cannot delete a state if stats exist for it.
ALTER TABLE state_annual_stats
    ADD CONSTRAINT fk_state_stats_state
    FOREIGN KEY (state_id)
    REFERENCES states (state_id)
    ON DELETE RESTRICT
    ON UPDATE CASCADE;

-- ---- state_annual_stats → data_sources ----
ALTER TABLE state_annual_stats
    ADD CONSTRAINT fk_state_stats_source
    FOREIGN KEY (source_id)
    REFERENCES data_sources (source_id)
    ON DELETE RESTRICT
    ON UPDATE CASCADE;

-- ---- city_accident_stats → cities ----
ALTER TABLE city_accident_stats
    ADD CONSTRAINT fk_city_acc_city
    FOREIGN KEY (city_id)
    REFERENCES cities (city_id)
    ON DELETE RESTRICT
    ON UPDATE CASCADE;

-- ---- city_accident_stats → data_sources ----
ALTER TABLE city_accident_stats
    ADD CONSTRAINT fk_city_acc_source
    FOREIGN KEY (source_id)
    REFERENCES data_sources (source_id)
    ON DELETE RESTRICT
    ON UPDATE CASCADE;

-- ---- city_violation_stats → cities ----
ALTER TABLE city_violation_stats
    ADD CONSTRAINT fk_city_vio_city
    FOREIGN KEY (city_id)
    REFERENCES cities (city_id)
    ON DELETE RESTRICT
    ON UPDATE CASCADE;

-- ---- city_violation_stats → violation_types ----
ALTER TABLE city_violation_stats
    ADD CONSTRAINT fk_city_vio_type
    FOREIGN KEY (violation_type_id)
    REFERENCES violation_types (violation_type_id)
    ON DELETE RESTRICT
    ON UPDATE CASCADE;

-- ---- city_violation_stats → data_sources ----
ALTER TABLE city_violation_stats
    ADD CONSTRAINT fk_city_vio_source
    FOREIGN KEY (source_id)
    REFERENCES data_sources (source_id)
    ON DELETE RESTRICT
    ON UPDATE CASCADE;

-- ---- city_weather_stats → cities ----
ALTER TABLE city_weather_stats
    ADD CONSTRAINT fk_city_wea_city
    FOREIGN KEY (city_id)
    REFERENCES cities (city_id)
    ON DELETE RESTRICT
    ON UPDATE CASCADE;

-- ---- city_weather_stats → weather_conditions ----
ALTER TABLE city_weather_stats
    ADD CONSTRAINT fk_city_wea_cond
    FOREIGN KEY (weather_condition_id)
    REFERENCES weather_conditions (weather_condition_id)
    ON DELETE RESTRICT
    ON UPDATE CASCADE;

-- ---- city_weather_stats → data_sources ----
ALTER TABLE city_weather_stats
    ADD CONSTRAINT fk_city_wea_source
    FOREIGN KEY (source_id)
    REFERENCES data_sources (source_id)
    ON DELETE RESTRICT
    ON UPDATE CASCADE;

-- ---- city_road_feature_stats → cities ----
ALTER TABLE city_road_feature_stats
    ADD CONSTRAINT fk_city_rf_city
    FOREIGN KEY (city_id)
    REFERENCES cities (city_id)
    ON DELETE RESTRICT
    ON UPDATE CASCADE;

-- ---- city_road_feature_stats → road_features ----
ALTER TABLE city_road_feature_stats
    ADD CONSTRAINT fk_city_rf_feat
    FOREIGN KEY (road_feature_id)
    REFERENCES road_features (road_feature_id)
    ON DELETE RESTRICT
    ON UPDATE CASCADE;

-- ---- city_road_feature_stats → data_sources ----
ALTER TABLE city_road_feature_stats
    ADD CONSTRAINT fk_city_rf_source
    FOREIGN KEY (source_id)
    REFERENCES data_sources (source_id)
    ON DELETE RESTRICT
    ON UPDATE CASCADE;

-- ---- collision_type_stats → collision_types ----
ALTER TABLE collision_type_stats
    ADD CONSTRAINT fk_coll_stats_type
    FOREIGN KEY (collision_type_id)
    REFERENCES collision_types (collision_type_id)
    ON DELETE RESTRICT
    ON UPDATE CASCADE;

-- ---- collision_type_stats → data_sources ----
ALTER TABLE collision_type_stats
    ADD CONSTRAINT fk_coll_stats_source
    FOREIGN KEY (source_id)
    REFERENCES data_sources (source_id)
    ON DELETE RESTRICT
    ON UPDATE CASCADE;

-- ---- violation_type_stats → violation_types ----
ALTER TABLE violation_type_stats
    ADD CONSTRAINT fk_viol_stats_type
    FOREIGN KEY (violation_type_id)
    REFERENCES violation_types (violation_type_id)
    ON DELETE RESTRICT
    ON UPDATE CASCADE;

-- ---- violation_type_stats → data_sources ----
ALTER TABLE violation_type_stats
    ADD CONSTRAINT fk_viol_stats_source
    FOREIGN KEY (source_id)
    REFERENCES data_sources (source_id)
    ON DELETE RESTRICT
    ON UPDATE CASCADE;

-- =============================================================
-- SECTION 4: CHECK CONSTRAINTS
-- =============================================================

-- Year range checks — Indian road accident data exists from 1970 onward
ALTER TABLE national_historical_stats
    ADD CONSTRAINT chk_nat_hist_year
    CHECK (year BETWEEN 1970 AND 2030);

ALTER TABLE national_annual_stats
    ADD CONSTRAINT chk_nat_ann_year
    CHECK (year BETWEEN 2019 AND 2030);

ALTER TABLE state_annual_stats
    ADD CONSTRAINT chk_state_year
    CHECK (year BETWEEN 2019 AND 2030);

ALTER TABLE city_accident_stats
    ADD CONSTRAINT chk_city_acc_year
    CHECK (year BETWEEN 2019 AND 2030);

ALTER TABLE city_violation_stats
    ADD CONSTRAINT chk_city_vio_year
    CHECK (year BETWEEN 2019 AND 2030);

ALTER TABLE city_weather_stats
    ADD CONSTRAINT chk_city_wea_year
    CHECK (year BETWEEN 2019 AND 2030);

ALTER TABLE city_road_feature_stats
    ADD CONSTRAINT chk_city_rf_year
    CHECK (year BETWEEN 2019 AND 2030);

ALTER TABLE collision_type_stats
    ADD CONSTRAINT chk_coll_year
    CHECK (year BETWEEN 2019 AND 2030);

ALTER TABLE violation_type_stats
    ADD CONSTRAINT chk_viol_year
    CHECK (year BETWEEN 2019 AND 2030);

-- Non-negative accident counts (already in CREATE TABLE for some, repeated here as named)
-- Non-negative checks for national_historical_stats
ALTER TABLE national_historical_stats
    ADD CONSTRAINT chk_nat_hist_accidents    CHECK (total_accidents  IS NULL OR total_accidents  >= 0);
ALTER TABLE national_historical_stats
    ADD CONSTRAINT chk_nat_hist_killed       CHECK (total_killed     IS NULL OR total_killed     >= 0);
ALTER TABLE national_historical_stats
    ADD CONSTRAINT chk_nat_hist_injured      CHECK (total_injured    IS NULL OR total_injured    >= 0);
ALTER TABLE national_historical_stats
    ADD CONSTRAINT chk_nat_hist_population   CHECK (population_thousands IS NULL OR population_thousands >= 0);

ALTER TABLE national_annual_stats
    ADD CONSTRAINT chk_nat_ann_accidents     CHECK (total_accidents  >= 0);
ALTER TABLE national_annual_stats
    ADD CONSTRAINT chk_nat_ann_fatalities    CHECK (total_fatalities >= 0);
ALTER TABLE national_annual_stats
    ADD CONSTRAINT chk_nat_ann_injured       CHECK (total_injured    >= 0);

ALTER TABLE state_annual_stats
    ADD CONSTRAINT chk_state_acc_count       CHECK (accident_count  IS NULL OR accident_count  >= 0);
ALTER TABLE state_annual_stats
    ADD CONSTRAINT chk_state_killed          CHECK (persons_killed   IS NULL OR persons_killed  >= 0);
ALTER TABLE state_annual_stats
    ADD CONSTRAINT chk_state_acc_rank        CHECK (accident_rank   IS NULL OR accident_rank   BETWEEN 1 AND 50);
ALTER TABLE state_annual_stats
    ADD CONSTRAINT chk_state_kill_rank       CHECK (killed_rank     IS NULL OR killed_rank     BETWEEN 1 AND 50);

ALTER TABLE city_accident_stats
    ADD CONSTRAINT chk_city_acc_rank         CHECK (accident_rank  IS NULL OR accident_rank  BETWEEN 1 AND 50);
ALTER TABLE city_accident_stats
    ADD CONSTRAINT chk_city_kill_rank        CHECK (killed_rank    IS NULL OR killed_rank    BETWEEN 1 AND 50);
ALTER TABLE city_accident_stats
    ADD CONSTRAINT chk_city_inj_rank         CHECK (injured_rank   IS NULL OR injured_rank   BETWEEN 1 AND 50);

-- =============================================================
-- SECTION 5: NOT NULL CONSTRAINTS (supplementary — inline NOTs NULLS
--   already in CREATE TABLE for critical columns; this section
--   adds any missed ones and documents decisions)
-- =============================================================

-- data_sources: source_file and source_directory are mandatory
-- (already NOT NULL in CREATE TABLE)

-- states: state_name and state_type are mandatory
-- (already NOT NULL in CREATE TABLE)

-- cities: city_name is mandatory; state_id is nullable (unverified states)
-- (already NOT NULL for city_name in CREATE TABLE)
