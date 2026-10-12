-- =============================================================
-- ROAD INSIGHT — PostgreSQL Database
-- File: 01_create_schema.sql
-- Purpose: Create the road_insight schema and supporting types
-- Author: Data Engineering Team
-- Date: 2026-09-21
-- =============================================================

-- Drop and recreate for idempotent setup
-- WARNING: DROP SCHEMA will destroy all objects in the schema.
-- Comment out or remove in production if data must be preserved.

-- CREATE SCHEMA IF NOT EXISTS road_insight;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.schemata
        WHERE schema_name = 'road_insight'
    ) THEN
        CREATE SCHEMA road_insight;
        RAISE NOTICE 'Schema road_insight created.';
    ELSE
        RAISE NOTICE 'Schema road_insight already exists.';
    END IF;
END;
$$;

-- Set search path for subsequent statements in this session
SET search_path TO road_insight, public;

-- =============================================================
-- COMMENTS
-- =============================================================
COMMENT ON SCHEMA road_insight IS
    'Production schema for ROAD INSIGHT — AI-Powered Indian Road Accident Analysis System. '
    'Contains normalized OLTP tables, staging tables, and reference data. '
    'Sources: MoRTH Road Accident reports 2019-2023.';
