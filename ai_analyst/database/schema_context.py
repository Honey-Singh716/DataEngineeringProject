"""
ai_analyst/database/schema_context.py
Complete, verified schema context for the 15 LLM-approved analytical tables.

SCHEMA_CONTEXT_TEXT  – multi-line string injected into the system prompt.
ALLOWED_TABLES       – canonical set used by the SQL validator.
ALLOWED_SCHEMA       – the only permitted schema name.

All definitions were verified against the live roadinsight PostgreSQL 17.10
database during the ROAD_INSIGHT_DATABASE_AUDIT (November 2026).
Staging tables (stg_*) are intentionally excluded.
"""
from __future__ import annotations

# ── Schema and allowlist ────────────────────────────────────────────────────

ALLOWED_SCHEMA: str = "road_insight"

ALLOWED_TABLES: frozenset[str] = frozenset(
    {
        "states",
        "cities",
        "violation_types",
        "collision_types",
        "road_features",
        "weather_conditions",
        "state_annual_stats",
        "city_accident_stats",
        "city_violation_stats",
        "city_weather_stats",
        "city_road_feature_stats",
        "violation_type_stats",
        "collision_type_stats",
        "national_annual_stats",
        "national_historical_stats",
        # Approved 7 analytical views (read-only, safe, no data_sources dependency)
        "vw_state_yoy_comparison",
        "vw_national_trends",
        "vw_city_violation_summary",
        "vw_city_weather_summary",
        "vw_city_road_feature_summary",
        "vw_collision_type_summary",
        "vw_violation_type_summary",
    }
)

# ── Canonical schema context text injected into the LLM system prompt ───────

SCHEMA_CONTEXT_TEXT: str = """
Database  : roadinsight
Schema    : road_insight
Source    : MoRTH (Ministry of Road Transport & Highways), Government of India
Audit date: November 2026

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MASTER DIMENSION TABLES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

road_insight.states
  Rows: 37  (28 States + 9 Union Territories)
  Columns:
    state_id    SMALLINT  PK  – surrogate key
    state_name  VARCHAR   UK  – official name, e.g. 'Maharashtra', 'Delhi'
    state_type  VARCHAR       – values: 'State' | 'Union Territory'
    is_active   BOOLEAN       – FALSE only for Daman & Diu (merged 2020)
    notes       TEXT          – administrative notes
  IMPORTANT: Always add "WHERE s.is_active = true" for current analysis.

road_insight.cities
  Rows: 50  (million-plus cities only)
  Columns:
    city_id    SMALLINT  PK
    city_name  VARCHAR   UK  – e.g. 'Delhi', 'Bengaluru', 'Mumbai'
    state_id   SMALLINT  FK → states.state_id
  NOTE: These 50 cities do NOT represent all of India; their accident
        totals do NOT sum to state or national totals.

road_insight.violation_types
  Rows: 6
  Columns:
    violation_type_id    SMALLINT  PK
    violation_type_name  VARCHAR   UK
    description          TEXT
  Values: 'Over-speeding' | 'Drunken driving/consumption of alcohol & drug' |
          'Driving on wrong side/Lane indiscipline' | 'Jumping red light' |
          'Use of mobile phone' | 'Others'

road_insight.collision_types
  Rows: 9
  Columns:
    collision_type_id    SMALLINT  PK
    collision_type_name  VARCHAR   UK
    description          TEXT
  Values: 'Hit and Run' | 'With parked Vehicle' | 'Hit from Back' |
          'Hit from side' | 'Run off Road' | 'Fixed object' |
          'Vehicle overturn' | 'Head on collision' | 'Others'

road_insight.weather_conditions
  Rows: 5
  Columns:
    weather_condition_id    SMALLINT  PK
    weather_condition_name  VARCHAR   UK
    description             TEXT
  Values: 'Sunny/Clear' | 'Rainy' | 'Foggy and Misty' | 'Hail/Sleet' |
          'Others'

road_insight.road_features
  Rows: 8
  Columns:
    road_feature_id    SMALLINT  PK
    road_feature_name  VARCHAR   UK
    description        TEXT
  Values: 'Straight Road' | 'Curved Road' | 'Bridge' | 'Culvert' |
          'Pot Holes' | 'Steep Grade' |
          'Ongoing Road Works/Under Construction' | 'Others'

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FACT / STATISTICAL TABLES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

road_insight.state_annual_stats
  Rows: 185  (37 states × 5 years)
  Years: 2019 – 2023
  Grain: one row per (state, year)
  Columns:
    stat_id        BIGINT    PK
    state_id       SMALLINT  FK → states.state_id
    year           SMALLINT  NOT NULL
    source_id      SMALLINT  FK → data_sources.source_id
    accident_count INTEGER   – total road accidents (may be NULL for merged UTs)
    accident_rank  SMALLINT  – national rank (1 = most accidents)
    persons_killed INTEGER   – total fatalities (may be NULL)
    killed_rank    SMALLINT  – national rank (1 = most killed)
    loaded_at      TIMESTAMPTZ
  JOINS: JOIN road_insight.states s ON sas.state_id = s.state_id

road_insight.city_accident_stats
  Rows: 100  (50 cities × 2 years)
  Years: 2022 – 2023
  Grain: one row per (city, year)
  Columns:
    stat_id         BIGINT    PK
    city_id         SMALLINT  FK → cities.city_id
    year            SMALLINT  NOT NULL
    source_id       SMALLINT  FK → data_sources.source_id
    accident_count  INTEGER   NOT NULL
    persons_killed  INTEGER   NOT NULL
    persons_injured INTEGER   NOT NULL
    accident_rank   SMALLINT  – 50-city rank
    killed_rank     SMALLINT
    injured_rank    SMALLINT
    loaded_at       TIMESTAMPTZ
  JOINS: JOIN road_insight.cities c ON cas.city_id = c.city_id
         JOIN road_insight.states s ON c.state_id = s.state_id

road_insight.city_violation_stats
  Rows: 300  (50 cities × 6 violation types)
  Years: 2023 only
  Grain: one row per (city, year, violation_type)
  Columns:
    stat_id           BIGINT    PK
    city_id           SMALLINT  FK → cities.city_id
    year              SMALLINT  NOT NULL
    violation_type_id SMALLINT  FK → violation_types.violation_type_id
    source_id         SMALLINT  FK → data_sources.source_id
    accident_count    INTEGER   NOT NULL – accidents caused by this violation
    loaded_at         TIMESTAMPTZ
  JOINS: JOIN road_insight.violation_types vt ON cvs.violation_type_id = vt.violation_type_id
         JOIN road_insight.cities c ON cvs.city_id = c.city_id

road_insight.city_weather_stats
  Rows: 250  (50 cities × 5 weather conditions)
  Years: 2019 only
  Grain: one row per (city, year, weather_condition)
  Columns:
    stat_id                   BIGINT    PK
    city_id                   SMALLINT  FK → cities.city_id
    year                      SMALLINT  NOT NULL  DEFAULT 2019
    weather_condition_id      SMALLINT  FK → weather_conditions.weather_condition_id
    source_id                 SMALLINT  FK → data_sources.source_id
    accident_count            INTEGER   NOT NULL
    persons_killed            INTEGER   NOT NULL
    persons_grievously_injured INTEGER  NOT NULL
    persons_minor_injured     INTEGER   NOT NULL
    persons_total_injured     INTEGER   NOT NULL
    loaded_at                 TIMESTAMPTZ
  JOINS: JOIN road_insight.weather_conditions wc ON cws.weather_condition_id = wc.weather_condition_id
         JOIN road_insight.cities c ON cws.city_id = c.city_id

road_insight.city_road_feature_stats
  Rows: 400  (50 cities × 8 road features)
  Years: 2019 only
  Grain: one row per (city, year, road_feature)
  Columns:
    stat_id                    BIGINT    PK
    city_id                    SMALLINT  FK → cities.city_id
    year                       SMALLINT  NOT NULL  DEFAULT 2019
    road_feature_id            SMALLINT  FK → road_features.road_feature_id
    source_id                  SMALLINT  FK → data_sources.source_id
    accident_count             INTEGER   NOT NULL
    persons_killed             INTEGER   NOT NULL
    persons_grievously_injured INTEGER   NOT NULL
    persons_minor_injured      INTEGER   NOT NULL
    persons_total_injured      INTEGER   NOT NULL
    loaded_at                  TIMESTAMPTZ
  JOINS: JOIN road_insight.road_features rf ON crfs.road_feature_id = rf.road_feature_id
         JOIN road_insight.cities c ON crfs.city_id = c.city_id

road_insight.violation_type_stats
  Rows: 12  (6 violation types × 2 years)
  Years: 2022 – 2023
  Grain: one row per (violation_type, year)
  Columns:
    stat_id           BIGINT    PK
    violation_type_id SMALLINT  FK → violation_types.violation_type_id
    year              SMALLINT  NOT NULL
    source_id         SMALLINT  FK → data_sources.source_id
    accident_count    INTEGER   NOT NULL – NATIONAL total
    persons_killed    INTEGER   NOT NULL
    persons_injured   INTEGER   NOT NULL
    loaded_at         TIMESTAMPTZ
  JOINS: JOIN road_insight.violation_types vt ON vts.violation_type_id = vt.violation_type_id

road_insight.collision_type_stats
  Rows: 18  (9 collision types × 2 years)
  Years: 2022 – 2023
  Grain: one row per (collision_type, year)
  Columns:
    stat_id           BIGINT    PK
    collision_type_id SMALLINT  FK → collision_types.collision_type_id
    year              SMALLINT  NOT NULL
    source_id         SMALLINT  FK → data_sources.source_id
    accident_count    INTEGER   NOT NULL – NATIONAL total
    persons_killed    INTEGER   NOT NULL
    persons_injured   INTEGER   NOT NULL
    loaded_at         TIMESTAMPTZ
  JOINS: JOIN road_insight.collision_types ct ON cts.collision_type_id = ct.collision_type_id

road_insight.national_annual_stats
  Rows: 5  (one per year)
  Years: 2019 – 2023
  Grain: one row per year (national consolidated)
  Columns:
    stat_id              BIGINT    PK
    year                 SMALLINT  UK  NOT NULL
    source_id            SMALLINT  FK → data_sources.source_id
    total_accidents      INTEGER   NOT NULL
    total_fatalities     INTEGER   NOT NULL   ← use this column name (not persons_killed)
    total_injured        INTEGER   NOT NULL
    accidents_pct_change NUMERIC(5,2) – YoY % change (can be negative)
    fatalities_pct_change NUMERIC(5,2)
    injured_pct_change   NUMERIC(5,2)
    loaded_at            TIMESTAMPTZ

road_insight.national_historical_stats
  Rows: 29  (1970 – 2019 inclusive, 50 years minus gaps)
  Years: 1970 – 2019
  Grain: one row per year (national long-term time series)
  Columns:
    stat_id                              BIGINT    PK
    year                                 SMALLINT  UK  NOT NULL
    source_id                            SMALLINT  FK → data_sources.source_id
    total_accidents                      INTEGER
    fatal_accidents                      INTEGER   – accidents where someone died
    total_killed                         INTEGER   ← use this column name (not persons_killed / total_fatalities)
    total_injured                        INTEGER
    population_thousands                 NUMERIC(12,3)
    registered_vehicles_thousands        NUMERIC(12,3)
    road_length_km                       NUMERIC(12,2)
    accidents_per_ten_thousand_vehicles  NUMERIC(8,4)
    killed_per_ten_thousand_vehicles     NUMERIC(8,4)
    accidents_per_lakh_pop               NUMERIC(8,4)
    killed_per_lakh_pop                  NUMERIC(8,4)
    injured_per_lakh_pop                 NUMERIC(8,4)
    loaded_at                            TIMESTAMPTZ

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PRE-BUILT ANALYTICAL VIEWS (safe to query)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  road_insight.vw_state_yoy_comparison    – YoY accident & fatality changes per state
  road_insight.vw_national_trends         – combined 1970-2023 national time-series
  road_insight.vw_city_violation_summary  – city violations with % share
  road_insight.vw_city_weather_summary    – city weather breakdown with fatality rate %
  road_insight.vw_city_road_feature_summary – city road-feature breakdown
  road_insight.vw_collision_type_summary  – collision types with % of national total
  road_insight.vw_violation_type_summary  – violation types with % of national total

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
KEY BUSINESS DEFINITIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Fatality rate  : ROUND(persons_killed::numeric / NULLIF(accident_count,0) * 100, 2)
                 → deaths per 100 accidents (severity metric)
Per lakh pop   : (count / population_thousands * 10) → national historical only
Accident count : raw total accidents (not rate-adjusted)
Rank=1         : most accidents / most killed (worst performer)
""".strip()

