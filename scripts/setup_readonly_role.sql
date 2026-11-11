-- ============================================================================
-- ROAD INSIGHT: Read-Only Database Role Setup Script
-- File: scripts/setup_readonly_role.sql
-- 
-- PURPOSE:
-- Creates a dedicated, unprivileged read-only role for the LLM Text-to-SQL
-- query engine, enforcing database-level least-privilege safety boundaries:
--   1. Explicit SELECT permissions ONLY on 15 approved analytical tables and
--      7 approved analytical views (no broad schema-wide grants).
--   2. Explicitly blocks data_sources, dependent views, and staging tables.
--   3. No automatic future-table grants (ALTER DEFAULT PRIVILEGES removed).
--   4. Enforces session-level read-only transactions (default_transaction_read_only = on).
--   5. Enforces a 3-second statement timeout (statement_timeout = '3000ms').
--
-- EXECUTION:
-- Run this script as a PostgreSQL superuser in psql:
--   psql -U postgres -d roadinsight -v ro_password="<secure_password>" -f scripts/setup_readonly_role.sql
-- ============================================================================

\c roadinsight;

-- Validate that ro_password was provided
\if :{?ro_password}
\else
    \echo '========================================================================'
    \echo 'ERROR: Variable ro_password is not set!'
    \echo 'Usage: psql -U postgres -d roadinsight -v ro_password="<password>" -f scripts/setup_readonly_role.sql'
    \echo '========================================================================'
    \set ON_ERROR_STOP on
    SELECT 'ro_password parameter is required'::integer;
\endif

-- 1. Create or update the read-only role
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'roadinsight_readonly') THEN
        CREATE ROLE roadinsight_readonly WITH LOGIN;
    END IF;
END
$$;

ALTER ROLE roadinsight_readonly WITH PASSWORD :'ro_password';

-- 2. Revoke any prior broad or inherited privileges
REVOKE ALL PRIVILEGES ON ALL TABLES IN SCHEMA road_insight FROM roadinsight_readonly;
REVOKE ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA road_insight FROM roadinsight_readonly;
REVOKE ALL PRIVILEGES ON SCHEMA road_insight FROM roadinsight_readonly;
REVOKE ALL PRIVILEGES ON SCHEMA public FROM roadinsight_readonly;
REVOKE TEMP, TEMPORARY ON DATABASE roadinsight FROM roadinsight_readonly;

-- 3. Configure connection and schema usage
GRANT CONNECT ON DATABASE roadinsight TO roadinsight_readonly;
GRANT USAGE ON SCHEMA road_insight TO roadinsight_readonly;

-- 4. Explicit least-privilege SELECT grants: 15 approved analytical tables
GRANT SELECT ON TABLE road_insight.states TO roadinsight_readonly;
GRANT SELECT ON TABLE road_insight.cities TO roadinsight_readonly;
GRANT SELECT ON TABLE road_insight.violation_types TO roadinsight_readonly;
GRANT SELECT ON TABLE road_insight.collision_types TO roadinsight_readonly;
GRANT SELECT ON TABLE road_insight.road_features TO roadinsight_readonly;
GRANT SELECT ON TABLE road_insight.weather_conditions TO roadinsight_readonly;
GRANT SELECT ON TABLE road_insight.state_annual_stats TO roadinsight_readonly;
GRANT SELECT ON TABLE road_insight.city_accident_stats TO roadinsight_readonly;
GRANT SELECT ON TABLE road_insight.city_violation_stats TO roadinsight_readonly;
GRANT SELECT ON TABLE road_insight.city_weather_stats TO roadinsight_readonly;
GRANT SELECT ON TABLE road_insight.city_road_feature_stats TO roadinsight_readonly;
GRANT SELECT ON TABLE road_insight.collision_type_stats TO roadinsight_readonly;
GRANT SELECT ON TABLE road_insight.violation_type_stats TO roadinsight_readonly;
GRANT SELECT ON TABLE road_insight.national_annual_stats TO roadinsight_readonly;
GRANT SELECT ON TABLE road_insight.national_historical_stats TO roadinsight_readonly;

-- 5. Explicit least-privilege SELECT grants: 7 approved analytical views
-- (vw_state_stats_full and vw_city_stats_full are excluded as they expose data_sources)
GRANT SELECT ON TABLE road_insight.vw_state_yoy_comparison TO roadinsight_readonly;
GRANT SELECT ON TABLE road_insight.vw_national_trends TO roadinsight_readonly;
GRANT SELECT ON TABLE road_insight.vw_city_violation_summary TO roadinsight_readonly;
GRANT SELECT ON TABLE road_insight.vw_city_weather_summary TO roadinsight_readonly;
GRANT SELECT ON TABLE road_insight.vw_city_road_feature_summary TO roadinsight_readonly;
GRANT SELECT ON TABLE road_insight.vw_collision_type_summary TO roadinsight_readonly;
GRANT SELECT ON TABLE road_insight.vw_violation_type_summary TO roadinsight_readonly;

-- 6. Enforce execution guardrails at the role level
ALTER ROLE roadinsight_readonly SET default_transaction_read_only = on;
ALTER ROLE roadinsight_readonly SET statement_timeout = '3000ms';
ALTER ROLE roadinsight_readonly SET search_path = road_insight, public;

-- 7. Verification output
SELECT rolname, rolsuper, rolcreaterole, rolcreatedb, rolinherit, rolcanlogin 
FROM pg_roles 
WHERE rolname = 'roadinsight_readonly';
