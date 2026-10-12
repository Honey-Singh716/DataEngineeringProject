-- =============================================================
-- ROAD INSIGHT — PostgreSQL Database
-- File: 02_create_tables.sql
-- Purpose: Create all normalized tables
-- Run after: 01_create_schema.sql
-- =============================================================

SET search_path TO road_insight, public;

-- =============================================================
-- SECTION A: DATA PROVENANCE
-- =============================================================

CREATE TABLE IF NOT EXISTS data_sources (
    source_id         SMALLINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source_file       VARCHAR(255) NOT NULL,
    source_directory  VARCHAR(255) NOT NULL,
    description       TEXT,
    report_year       SMALLINT,         -- Publication year of the report
    data_year_min     SMALLINT,         -- Minimum year of data coverage
    data_year_max     SMALLINT,         -- Maximum year of data coverage
    geographic_scope  VARCHAR(100),     -- 'National', 'State', 'City'
    notes             TEXT,
    loaded_at         TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE data_sources IS
    'Tracks every source CSV/XLSX file loaded into the database. '
    'Allows traceability from any database record back to its source file.';

COMMENT ON COLUMN data_sources.report_year IS
    'Year the source report was published (e.g., 2023 for MoRTH 2023 report).';
COMMENT ON COLUMN data_sources.data_year_min IS
    'Earliest year of data covered in this file.';
COMMENT ON COLUMN data_sources.data_year_max IS
    'Latest year of data covered in this file.';

-- =============================================================
-- SECTION B: DIMENSION TABLES
-- =============================================================

-- ------------------------------------------------------------
-- B1. States / Union Territories
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS states (
    state_id      SMALLINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    state_name    VARCHAR(100) NOT NULL,
    state_type    VARCHAR(30) NOT NULL
                  CHECK (state_type IN ('State', 'Union Territory')),
    is_active     BOOLEAN NOT NULL DEFAULT TRUE,
    notes         TEXT    -- For footnotes (e.g., "Ladakh data included in J&K for 2019-2020")
);

COMMENT ON TABLE states IS
    'Reference table for all Indian States and Union Territories. '
    '37 states/UTs present in source data.';

COMMENT ON COLUMN states.state_type IS
    'Whether the entity is a State or Union Territory under Indian law.';
COMMENT ON COLUMN states.is_active IS
    'FALSE if the entity has been merged or reorganized (e.g., Daman & Diu).';
COMMENT ON COLUMN states.notes IS
    'Stores official footnotes from source data about data coverage changes.';

-- ------------------------------------------------------------
-- B2. Cities (Large Cities — 50 cities tracked by MoRTH)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS cities (
    city_id       SMALLINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    city_name     VARCHAR(100) NOT NULL,
    state_id      SMALLINT                -- FK to states; NULL if state unknown/unverified
);

COMMENT ON TABLE cities IS
    'Reference table for 50 large Indian cities tracked in MoRTH city-level reports. '
    'State association added where determinable.';

COMMENT ON COLUMN cities.state_id IS
    'Foreign key to states table. Allows querying city stats by state. '
    'Set to NULL if state assignment is uncertain.';

-- ------------------------------------------------------------
-- B3. Weather Conditions (for city-level 2019 data)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS weather_conditions (
    weather_condition_id    SMALLINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    weather_condition_name  VARCHAR(50) NOT NULL UNIQUE,
    description             TEXT
);

COMMENT ON TABLE weather_conditions IS
    'Reference lookup for weather conditions at time of accident. '
    'Source: RA2019_A45.csv. Values: Sunny/Clear, Rainy, Foggy and Misty, Hail/Sleet, Others.';

-- ------------------------------------------------------------
-- B4. Road Feature Types (for city-level 2019 data)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS road_features (
    road_feature_id    SMALLINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    road_feature_name  VARCHAR(100) NOT NULL UNIQUE,
    description        TEXT
);

COMMENT ON TABLE road_features IS
    'Reference lookup for road infrastructure feature types at accident locations. '
    'Source: RA2019_A48.csv. Values: Straight Road, Curved Road, Bridge, Culvert, etc.';

-- ------------------------------------------------------------
-- B5. Collision Types
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS collision_types (
    collision_type_id    SMALLINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    collision_type_name  VARCHAR(100) NOT NULL UNIQUE,
    description          TEXT
);

COMMENT ON TABLE collision_types IS
    'Reference lookup for types of road collisions. '
    'Source: RoadTypeColl.csv. '
    'Values: Hit and Run, With parked Vehicle, Hit from Back, etc.';

-- ------------------------------------------------------------
-- B6. Violation Types (Traffic Violation Causes)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS violation_types (
    violation_type_id    SMALLINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    violation_type_name  VARCHAR(150) NOT NULL UNIQUE,
    description          TEXT
);

COMMENT ON TABLE violation_types IS
    'Reference lookup for traffic violation categories causing accidents. '
    'Source: RoadTypeViol.csv, LargeCitiesVio.csv. '
    'Values: Over-speeding, Drunken driving, Wrong side, etc.';

-- =============================================================
-- SECTION C: FACT / AGGREGATE TABLES
-- =============================================================

-- ------------------------------------------------------------
-- C1. National Historical Statistics (RA2019_A1.csv)
--     Grain: 1 row = 1 year (national totals)
--     Years: 1970-2019 (with gaps)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS national_historical_stats (
    stat_id                        BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    year                           SMALLINT NOT NULL,
    source_id                      SMALLINT NOT NULL,

    -- Raw measures
    total_accidents                INTEGER,
    total_killed                   INTEGER,
    total_injured                  INTEGER,

    -- Context / denominators
    population_thousands           NUMERIC(12,3),  -- Population in thousands
    registered_vehicles_thousands  NUMERIC(12,3),  -- Vehicles in thousands
    road_length_km                 NUMERIC(12,3),  -- Road length in km (NULL for 2019)

    -- Derived rate columns (stored for historical reference / LLM queries)
    accidents_per_lakh_pop         NUMERIC(12,6),
    accidents_per_10k_vehicles     NUMERIC(12,6),
    accidents_per_10k_km_roads     NUMERIC(12,6),  -- NULL where road_length unavailable
    killed_per_lakh_pop            NUMERIC(12,6),
    killed_per_10k_vehicles        NUMERIC(12,6),
    killed_per_10k_km_roads        NUMERIC(12,6),
    injured_per_lakh_pop           NUMERIC(12,6),
    injured_per_10k_vehicles       NUMERIC(12,6),
    injured_per_10k_km_roads       NUMERIC(12,6),

    loaded_at                      TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE national_historical_stats IS
    'National road accident statistics from 1970 to 2019. '
    'One row per year. Includes absolute counts and per-capita/per-vehicle rates. '
    'Source: RA2019_A1.csv (MoRTH Road Accident Report 2019, Annexure 1).';

COMMENT ON COLUMN national_historical_stats.year IS
    'Calendar year. Not every year between 1970 and 1993 is present — '
    'data only available for 1970, 1980, 1990, then annually from 1994.';
COMMENT ON COLUMN national_historical_stats.road_length_km IS
    'NULL for 2019 — data not available in source.';
COMMENT ON COLUMN national_historical_stats.accidents_per_10k_km_roads IS
    'NULL for 2019 due to missing road length data.';

-- ------------------------------------------------------------
-- C2. National Annual Statistics (RoadNoAcc.csv)
--     Grain: 1 row = 1 year (national totals)
--     Years: 2019-2023
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS national_annual_stats (
    stat_id               BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    year                  SMALLINT NOT NULL,
    source_id             SMALLINT NOT NULL,

    total_accidents       INTEGER NOT NULL,
    total_fatalities      INTEGER NOT NULL,
    total_injured         INTEGER NOT NULL,

    -- YoY % changes (stored; derived from prior year row)
    accidents_pct_change  NUMERIC(6,2),   -- NULL for first year in series
    fatalities_pct_change NUMERIC(6,2),
    injured_pct_change    NUMERIC(6,2),

    loaded_at             TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE national_annual_stats IS
    'National road accident summary statistics for 2019-2023. '
    'One row per year. YoY percentage changes stored from source. '
    'Source: RoadNoAcc.csv. '
    'NOTE: 2019 data overlaps with national_historical_stats; both are retained '
    'for data provenance and because national_historical_stats has additional context columns.';

-- ------------------------------------------------------------
-- C3. State Annual Statistics
--     Grain: 1 row = 1 state × 1 year
--     Sources: RoadStateWiseAcc.csv + RoadStatewiseKilled.csv (merged)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS state_annual_stats (
    stat_id             BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    state_id            SMALLINT NOT NULL,
    year                SMALLINT NOT NULL,
    source_id           SMALLINT NOT NULL,

    -- From RoadStateWiseAcc.csv
    accident_count      INTEGER,      -- NULL where data not reported (Ladakh 2019-2020, Daman & Diu)
    accident_rank       SMALLINT,     -- Rank among states for that year; NULL where unavailable

    -- From RoadStatewiseKilled.csv
    persons_killed      INTEGER,      -- NULL where data not reported
    killed_rank         SMALLINT,     -- Rank by killed

    loaded_at           TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE state_annual_stats IS
    'State/UT level road accident and fatality statistics for 2019-2023. '
    'One row per state per year. NULLs where data not reported. '
    'Sources: RoadStateWiseAcc.csv + RoadStatewiseKilled.csv (joined on state + year).';

COMMENT ON COLUMN state_annual_stats.accident_count IS
    'NULL for Ladakh (2019-2020) — included in J&K figures those years. '
    'NULL for Daman & Diu (2020+) — merged into Dadra & Nagar Haveli UT.';
COMMENT ON COLUMN state_annual_stats.accident_rank IS
    'Rank of state among all states/UTs for accident count. '
    'NULL where not reported (same conditions as accident_count NULLs).';

-- ------------------------------------------------------------
-- C4. City Annual Accident Statistics
--     Grain: 1 row = 1 city × 1 year
--     Source: LargeCities.csv (unpivoted)
--     Years: 2022, 2023
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS city_accident_stats (
    stat_id           BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    city_id           SMALLINT NOT NULL,
    year              SMALLINT NOT NULL,
    source_id         SMALLINT NOT NULL,

    accident_count    INTEGER NOT NULL,
    persons_killed    INTEGER NOT NULL,
    persons_injured   INTEGER NOT NULL,

    accident_rank     SMALLINT,  -- Rank among 50 cities
    killed_rank       SMALLINT,
    injured_rank      SMALLINT,

    loaded_at         TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE city_accident_stats IS
    'City-level road accident statistics for 50 large Indian cities, 2022 and 2023. '
    'One row per city per year. Ranking among 50 cities stored from source. '
    'Source: LargeCities.csv (unpivoted from wide format).';

-- ------------------------------------------------------------
-- C5. City Violation Statistics
--     Grain: 1 row = 1 city × 1 year × 1 violation type
--     Source: LargeCitiesVio.csv (unpivoted)
--     Year: 2023 (assumed — REQUIRES VERIFICATION)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS city_violation_stats (
    stat_id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    city_id              SMALLINT NOT NULL,
    year                 SMALLINT NOT NULL,
    violation_type_id    SMALLINT NOT NULL,
    source_id            SMALLINT NOT NULL,

    accident_count       INTEGER NOT NULL CHECK (accident_count >= 0),

    loaded_at            TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE city_violation_stats IS
    'Number of accidents attributed to each traffic violation type, by city. '
    'One row per city × year × violation type. '
    'Source: LargeCitiesVio.csv. '
    'NOTE: Year assumed 2023 from context — verify with source report.';

-- ------------------------------------------------------------
-- C6. City Weather Accident Statistics (2019)
--     Grain: 1 row = 1 city × 1 weather condition
--     Source: RA2019_A45.csv (unpivoted)
--     Year: 2019
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS city_weather_stats (
    stat_id                     BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    city_id                     SMALLINT NOT NULL,
    year                        SMALLINT NOT NULL DEFAULT 2019,
    weather_condition_id        SMALLINT NOT NULL,
    source_id                   SMALLINT NOT NULL,

    accident_count              INTEGER NOT NULL CHECK (accident_count >= 0),
    persons_killed              INTEGER NOT NULL CHECK (persons_killed >= 0),
    persons_grievously_injured  INTEGER NOT NULL CHECK (persons_grievously_injured >= 0),
    persons_minor_injured       INTEGER NOT NULL CHECK (persons_minor_injured >= 0),
    persons_total_injured       INTEGER NOT NULL CHECK (persons_total_injured >= 0),

    loaded_at                   TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE city_weather_stats IS
    'City-level accident statistics broken down by weather condition at time of accident. '
    'One row per city × weather condition. Year = 2019. '
    'Source: RA2019_A45.csv (unpivoted from wide format). '
    'NOTE: "Grievously" corrected from source typo "Greviously".';

COMMENT ON COLUMN city_weather_stats.persons_total_injured IS
    'Total injured = persons_grievously_injured + persons_minor_injured. '
    'Stored as provided by source. Minor discrepancies may exist.';

-- ------------------------------------------------------------
-- C7. City Road Feature Accident Statistics (2019)
--     Grain: 1 row = 1 city × 1 road feature type
--     Source: RA2019_A48.csv (unpivoted)
--     Year: 2019
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS city_road_feature_stats (
    stat_id                     BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    city_id                     SMALLINT NOT NULL,
    year                        SMALLINT NOT NULL DEFAULT 2019,
    road_feature_id             SMALLINT NOT NULL,
    source_id                   SMALLINT NOT NULL,

    accident_count              INTEGER NOT NULL CHECK (accident_count >= 0),
    persons_killed              INTEGER NOT NULL CHECK (persons_killed >= 0),
    persons_grievously_injured  INTEGER NOT NULL CHECK (persons_grievously_injured >= 0),
    persons_minor_injured       INTEGER NOT NULL CHECK (persons_minor_injured >= 0),
    persons_total_injured       INTEGER NOT NULL CHECK (persons_total_injured >= 0),

    loaded_at                   TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE city_road_feature_stats IS
    'City-level accident statistics broken down by road infrastructure feature. '
    'One row per city × road feature type. Year = 2019. '
    'Source: RA2019_A48.csv (unpivoted from wide format).';

-- ------------------------------------------------------------
-- C8. National Collision Type Statistics
--     Grain: 1 row = 1 collision type × 1 year
--     Source: RoadTypeColl.csv
--     Years: 2022, 2023
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS collision_type_stats (
    stat_id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    collision_type_id    SMALLINT NOT NULL,
    year                 SMALLINT NOT NULL,
    source_id            SMALLINT NOT NULL,

    accident_count       INTEGER NOT NULL CHECK (accident_count >= 0),
    persons_killed       INTEGER NOT NULL CHECK (persons_killed >= 0),
    persons_injured      INTEGER NOT NULL CHECK (persons_injured >= 0),

    loaded_at            TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE collision_type_stats IS
    'National accident statistics by collision type for 2022 and 2023. '
    'One row per collision type per year. '
    'Source: RoadTypeColl.csv (data rows only; % share rows excluded).';

-- ------------------------------------------------------------
-- C9. National Violation Type Statistics
--     Grain: 1 row = 1 violation type × 1 year
--     Source: RoadTypeViol.csv
--     Years: 2022, 2023
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS violation_type_stats (
    stat_id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    violation_type_id    SMALLINT NOT NULL,
    year                 SMALLINT NOT NULL,
    source_id            SMALLINT NOT NULL,

    accident_count       INTEGER NOT NULL CHECK (accident_count >= 0),
    persons_killed       INTEGER NOT NULL CHECK (persons_killed >= 0),
    persons_injured      INTEGER NOT NULL CHECK (persons_injured >= 0),

    loaded_at            TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE violation_type_stats IS
    'National accident statistics by traffic violation cause for 2022 and 2023. '
    'One row per violation type per year. '
    'Source: RoadTypeViol.csv.';

-- =============================================================
-- SECTION D: STAGING TABLES
-- =============================================================
-- Staging tables mirror the raw CSV structure before transformation.
-- They are prefixed with stg_ and are NOT normalized.
-- They are kept for audit and reprocessing purposes.

CREATE TABLE IF NOT EXISTS stg_large_cities (
    stg_id               BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source_id            SMALLINT,
    source_row           INTEGER,
    raw_sl_no            VARCHAR(20),
    raw_city             VARCHAR(100),
    raw_2022_accidents   VARCHAR(20),
    raw_2023_accidents   VARCHAR(20),
    raw_2022_ranking_acc VARCHAR(10),
    raw_2023_ranking_acc VARCHAR(10),
    raw_2022_killed      VARCHAR(20),
    raw_2023_killed      VARCHAR(20),
    raw_2022_ranking_kil VARCHAR(10),
    raw_2023_ranking_kil VARCHAR(10),
    raw_2022_injured     VARCHAR(20),
    raw_2023_injured     VARCHAR(20),
    raw_2022_ranking_inj VARCHAR(10),
    raw_2023_ranking_inj VARCHAR(10),
    is_excluded          BOOLEAN DEFAULT FALSE,
    exclusion_reason     TEXT,
    loaded_at            TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS stg_large_cities_vio (
    stg_id               BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source_id            SMALLINT,
    source_row           INTEGER,
    raw_sl_no            VARCHAR(20),
    raw_city             VARCHAR(100),
    raw_overspeeding     VARCHAR(20),
    raw_drunk_drug       VARCHAR(20),
    raw_wrong_side       VARCHAR(20),
    raw_red_light        VARCHAR(20),
    raw_mobile_phone     VARCHAR(20),
    raw_others           VARCHAR(20),
    is_excluded          BOOLEAN DEFAULT FALSE,
    exclusion_reason     TEXT,
    loaded_at            TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS stg_road_no_acc (
    stg_id               BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source_id            SMALLINT,
    source_row           INTEGER,
    raw_year             VARCHAR(10),
    raw_accidents        VARCHAR(20),
    raw_pct_change_acc   VARCHAR(20),
    raw_fatalities       VARCHAR(20),
    raw_pct_change_fat   VARCHAR(20),
    raw_injured          VARCHAR(20),
    raw_pct_change_inj   VARCHAR(20),
    is_excluded          BOOLEAN DEFAULT FALSE,
    exclusion_reason     TEXT,
    loaded_at            TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS stg_road_state_acc (
    stg_id               BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source_id            SMALLINT,
    source_row           INTEGER,
    raw_sl_no            VARCHAR(20),
    raw_state            VARCHAR(100),
    raw_2019_accidents   VARCHAR(20),
    raw_2020_accidents   VARCHAR(20),
    raw_2021_accidents   VARCHAR(20),
    raw_2022_accidents   VARCHAR(20),
    raw_2023_accidents   VARCHAR(20),
    raw_change_2022_2023 VARCHAR(20),
    raw_pct_change       VARCHAR(20),
    raw_2019_rank        VARCHAR(10),
    raw_2020_rank        VARCHAR(10),
    raw_2021_rank        VARCHAR(10),
    raw_2022_rank        VARCHAR(10),
    raw_2023_rank        VARCHAR(10),
    is_excluded          BOOLEAN DEFAULT FALSE,
    exclusion_reason     TEXT,
    loaded_at            TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS stg_road_state_killed (
    stg_id               BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source_id            SMALLINT,
    source_row           INTEGER,
    raw_sl_no            VARCHAR(20),
    raw_state            VARCHAR(100),
    raw_2019_killed      VARCHAR(20),
    raw_2020_killed      VARCHAR(20),
    raw_2021_killed      VARCHAR(20),
    raw_2022_killed      VARCHAR(20),
    raw_2023_killed      VARCHAR(20),
    raw_pct_change       VARCHAR(20),
    raw_2019_rank        VARCHAR(10),
    raw_2020_rank        VARCHAR(10),
    raw_2021_rank        VARCHAR(10),
    raw_2022_rank        VARCHAR(10),
    raw_2023_rank        VARCHAR(10),
    is_excluded          BOOLEAN DEFAULT FALSE,
    exclusion_reason     TEXT,
    loaded_at            TIMESTAMPTZ DEFAULT NOW()
);
