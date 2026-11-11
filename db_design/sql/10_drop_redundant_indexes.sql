-- =============================================================
-- ROAD INSIGHT — PostgreSQL Database
-- File: 10_drop_redundant_indexes.sql
-- Purpose: Safely drop verified duplicate and prefix-redundant indexes
-- Ref: docs/evidence/indexes/redundant_index_analysis.md
-- =============================================================

SET search_path TO road_insight, public;

-- 1. Drop Exact Duplicate Indexes (already backed by UNIQUE constraints)
DROP INDEX IF EXISTS road_insight.idx_nat_hist_year;         -- Duplicate of uq_nat_hist_year
DROP INDEX IF EXISTS road_insight.idx_nat_ann_year;          -- Duplicate of uq_nat_ann_year
DROP INDEX IF EXISTS road_insight.idx_state_stats_state_year;-- Duplicate of uq_state_year
DROP INDEX IF EXISTS road_insight.idx_city_acc_city_year;    -- Duplicate of uq_city_acc_year
DROP INDEX IF EXISTS road_insight.idx_city_vio_city_year_type;-- Duplicate of uq_city_vio_year_type

-- 2. Drop Leading-Prefix Redundant Indexes (satisfied by composite unique B-tree indexes)
DROP INDEX IF EXISTS road_insight.idx_state_stats_state_id;  -- Leading prefix of uq_state_year (state_id, year)
DROP INDEX IF EXISTS road_insight.idx_city_acc_city_id;      -- Leading prefix of uq_city_acc_year (city_id, year)
DROP INDEX IF EXISTS road_insight.idx_city_vio_city_id;      -- Leading prefix of uq_city_vio_year_type (city_id, ...)
DROP INDEX IF EXISTS road_insight.idx_city_wea_city_id;      -- Leading prefix of uq_city_weather (city_id, ...)
DROP INDEX IF EXISTS road_insight.idx_city_rf_city_id;       -- Leading prefix of uq_city_road_feat (city_id, ...)
DROP INDEX IF EXISTS road_insight.idx_coll_type_id;          -- Leading prefix of uq_coll_type_year (collision_type_id, year)
DROP INDEX IF EXISTS road_insight.idx_viol_type_id;          -- Leading prefix of uq_viol_type_year (violation_type_id, year)

