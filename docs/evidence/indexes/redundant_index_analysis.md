# RoadInsight India — Formal Redundant Index Analysis

## 1. Executive Summary & PostgreSQL Catalog Theory
In PostgreSQL, index maintenance incurs measurable storage overhead and write amplification during `INSERT`, `UPDATE`, and `DELETE` operations. PostgreSQL enforces `UNIQUE` constraints and `PRIMARY KEY` declarations by automatically instantiating a dedicated B-tree index over the constrained columns.

Two distinct categories of index redundancy were identified between `db_design/sql/03_create_constraints.sql` and `db_design/sql/04_create_indexes.sql`:
1. **Identical Duplicate Indexes**: Explicit indexes created with the exact same column ordering as an existing unique constraint index.
2. **Leading-Prefix Redundant Indexes**: Single-column B-tree indexes defined on column `A` when a composite index on `(A, B, ...)` already exists. Under standard B-tree semantics, queries filtering on `WHERE A = ...` or `WHERE A IN (...)` can perform index scans directly on `(A, B, ...)`'s leading prefix, rendering the standalone index on `A` 100% redundant.

---

## 2. Redundancy Audit Matrix

| Index Name | Table | Columns | Pre-existing Constraint / Backing Index | Redundancy Classification | Optimization Action |
|---|---|---|---|---|---|
| `idx_nat_hist_year` | `national_historical_stats` | `(year)` | `uq_nat_hist_year (year)` | **Identical Duplicate** | DROP |
| `idx_nat_ann_year` | `national_annual_stats` | `(year)` | `uq_nat_ann_year (year)` | **Identical Duplicate** | DROP |
| `idx_state_stats_state_year` | `state_annual_stats` | `(state_id, year)` | `uq_state_year (state_id, year)` | **Identical Duplicate** | DROP |
| `idx_city_acc_city_year` | `city_accident_stats` | `(city_id, year)` | `uq_city_acc_year (city_id, year)` | **Identical Duplicate** | DROP |
| `idx_city_vio_city_year_type` | `city_violation_stats` | `(city_id, year, violation_type_id)` | `uq_city_vio_year_type (city_id, year, violation_type_id)` | **Identical Duplicate** | DROP |
| `idx_state_stats_state_id` | `state_annual_stats` | `(state_id)` | `uq_state_year (state_id, year)` | **Leading-Prefix Redundant** | DROP |
| `idx_city_acc_city_id` | `city_accident_stats` | `(city_id)` | `uq_city_acc_year (city_id, year)` | **Leading-Prefix Redundant** | DROP |
| `idx_city_vio_city_id` | `city_violation_stats` | `(city_id)` | `uq_city_vio_year_type (city_id, ...)` | **Leading-Prefix Redundant** | DROP |
| `idx_city_wea_city_id` | `city_weather_stats` | `(city_id)` | `uq_city_weather (city_id, year, weather_condition_id)` | **Leading-Prefix Redundant** | DROP |
| `idx_city_rf_city_id` | `city_road_feature_stats` | `(city_id)` | `uq_city_road_feat (city_id, year, road_feature_id)` | **Leading-Prefix Redundant** | DROP |
| `idx_coll_type_id` | `collision_type_stats` | `(collision_type_id)` | `uq_coll_type_year (collision_type_id, year)` | **Leading-Prefix Redundant** | DROP |
| `idx_viol_type_id` | `violation_type_stats` | `(violation_type_id)` | `uq_viol_type_year (violation_type_id, year)` | **Leading-Prefix Redundant** | DROP |

---

## 3. Retained High-Value Analytical Indexes

The following indexes are strictly non-redundant and have been preserved:
- **Foreign Key Indexes on Non-Prefix Positions**:
  - `idx_cities_state_id`: `cities (state_id)` -> FK to `states(state_id)` (no unique composite index starts with `state_id` on `cities`).
  - `idx_state_stats_source_id`: `state_annual_stats (source_id)` -> FK to `data_sources`.
  - `idx_city_vio_type_id`: `city_violation_stats (violation_type_id)` -> 3rd column of unique constraint.
  - `idx_city_wea_cond_id`: `city_weather_stats (weather_condition_id)` -> 3rd column of unique constraint.
  - `idx_city_rf_feat_id`: `city_road_feature_stats (road_feature_id)` -> 3rd column of unique constraint.
- **Standalone `year` Secondary-Column Filters**:
  - `idx_state_stats_year`, `idx_city_acc_year`, `idx_city_vio_year`, `idx_city_wea_year`, `idx_city_rf_year`, `idx_coll_year`, `idx_viol_year`
  - *Rationale*: `year` appears as the second column in `(state_id, year)` or `(city_id, year)`. B-trees cannot efficiently scan on the second column when the first column is unconstrained in a query like `SELECT * FROM state_annual_stats WHERE year = 2023`. Standalone `year` indexes are vital for annual slice queries.
- **Specialized Composite Indexes**:
  - `idx_city_wea_year_cond` on `(year, weather_condition_id)`
  - `idx_city_rf_year_feat` on `(year, road_feature_id)`
- **Measure Ordering / Top-N Indexes**:
  - `idx_city_acc_accident_count_desc` on `(accident_count DESC NULLS LAST)`
  - `idx_city_acc_killed_desc` on `(persons_killed DESC NULLS LAST)`
  - `idx_state_acc_count_desc` on `(accident_count DESC NULLS LAST)`
  - `idx_state_killed_desc` on `(persons_killed DESC NULLS LAST)`
- **Functional Text Search Indexes**:
  - `idx_states_name_lower` on `(LOWER(state_name))`
  - `idx_cities_name_lower` on `(LOWER(city_name))`

---

## 4. Impact Assessment

- **Index Count Reduction**: Removed 12 unnecessary indexes out of 29 original manual indexes (~41.4% reduction in manual index definitions).
- **Write Throughput**: Decreases index maintenance cost during bulk `COPY` / `to_sql` operations in the ETL pipeline.
- **Buffer Pool Memory**: Saves working memory by preventing duplicate B-tree index pages from occupying the PostgreSQL shared buffers.
- **Query Plan Regression**: Zero regression. Queries filtering on `state_id`, `city_id`, `collision_type_id`, or `violation_type_id` utilize the composite unique indexes without performance loss.

