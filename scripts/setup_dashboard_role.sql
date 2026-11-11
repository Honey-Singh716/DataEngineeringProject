-- ============================================================================
-- ROAD INSIGHT: Dashboard Database Role Setup Script
-- File: scripts/setup_dashboard_role.sql
-- 
-- PURPOSE:
-- Creates a dedicated, least-privilege role for the Streamlit Analytics Dashboard:
--   1. Explicit SELECT permissions on all 16 non-staging analytical tables,
--      including data_sources (needed for full view joins).
--   2. Explicit SELECT permissions on all 9 analytical views.
--   3. Explicitly NO access to staging tables (stg_*).
--   4. Read-only transactions enforced (default_transaction_read_only = on).
--   5. Enforces a 10-second statement timeout (statement_timeout = '10000ms').
--   6. Password passed securely via psql variable dash_password.
--
-- EXECUTION:
--   psql -U postgres -d roadinsight -v dash_password="<secure_password>" -f scripts/setup_dashboard_role.sql
-- ============================================================================

\c roadinsight;

-- Validate that dash_password was provided
\if :{?dash_password}
\else
    \echo '========================================================================'
    \echo 'ERROR: Variable dash_password is not set!'
    \echo 'Usage: psql -U postgres -d roadinsight -v dash_password="<password>" -f scripts/setup_dashboard_role.sql'
    \echo '========================================================================'
    \set ON_ERROR_STOP on
    SELECT 'dash_password parameter is required'::integer;
\endif

-- 1. Create or update the dashboard role
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'roadinsight_dashboard') THEN
        CREATE ROLE roadinsight_dashboard WITH LOGIN;
    END IF;
END
$$;

ALTER ROLE roadinsight_dashboard WITH PASSWORD :'dash_password';

-- 2. Revoke any prior broad or inherited privileges
REVOKE ALL PRIVILEGES ON ALL TABLES IN SCHEMA road_insight FROM roadinsight_dashboard;
REVOKE ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA road_insight FROM roadinsight_dashboard;
REVOKE ALL PRIVILEGES ON SCHEMA road_insight FROM roadinsight_dashboard;
REVOKE ALL PRIVILEGES ON SCHEMA public FROM roadinsight_dashboard;
REVOKE TEMP, TEMPORARY ON DATABASE roadinsight FROM roadinsight_dashboard;

-- 3. Configure connection and schema usage
GRANT CONNECT ON DATABASE roadinsight TO roadinsight_dashboard;
GRANT USAGE ON SCHEMA road_insight TO roadinsight_dashboard;

-- 4. Explicit least-privilege SELECT grants: 16 analytical tables (NO stg_* tables)
GRANT SELECT ON TABLE road_insight.states TO roadinsight_dashboard;
GRANT SELECT ON TABLE road_insight.cities TO roadinsight_dashboard;
GRANT SELECT ON TABLE road_insight.violation_types TO roadinsight_dashboard;
GRANT SELECT ON TABLE road_insight.collision_types TO roadinsight_dashboard;
GRANT SELECT ON TABLE road_insight.road_features TO roadinsight_dashboard;
GRANT SELECT ON TABLE road_insight.weather_conditions TO roadinsight_dashboard;
GRANT SELECT ON TABLE road_insight.data_sources TO roadinsight_dashboard;
GRANT SELECT ON TABLE road_insight.state_annual_stats TO roadinsight_dashboard;
GRANT SELECT ON TABLE road_insight.city_accident_stats TO roadinsight_dashboard;
GRANT SELECT ON TABLE road_insight.city_violation_stats TO roadinsight_dashboard;
GRANT SELECT ON TABLE road_insight.city_weather_stats TO roadinsight_dashboard;
GRANT SELECT ON TABLE road_insight.city_road_feature_stats TO roadinsight_dashboard;
GRANT SELECT ON TABLE road_insight.collision_type_stats TO roadinsight_dashboard;
GRANT SELECT ON TABLE road_insight.violation_type_stats TO roadinsight_dashboard;
GRANT SELECT ON TABLE road_insight.national_annual_stats TO roadinsight_dashboard;
GRANT SELECT ON TABLE road_insight.national_historical_stats TO roadinsight_dashboard;

-- 5. Explicit least-privilege SELECT grants: all 9 analytical views
GRANT SELECT ON TABLE road_insight.vw_state_stats_full TO roadinsight_dashboard;
GRANT SELECT ON TABLE road_insight.vw_city_stats_full TO roadinsight_dashboard;
GRANT SELECT ON TABLE road_insight.vw_city_violation_summary TO roadinsight_dashboard;
GRANT SELECT ON TABLE road_insight.vw_national_trends TO roadinsight_dashboard;
GRANT SELECT ON TABLE road_insight.vw_collision_type_summary TO roadinsight_dashboard;
GRANT SELECT ON TABLE road_insight.vw_violation_type_summary TO roadinsight_dashboard;
GRANT SELECT ON TABLE road_insight.vw_city_weather_summary TO roadinsight_dashboard;
GRANT SELECT ON TABLE road_insight.vw_city_road_feature_summary TO roadinsight_dashboard;
GRANT SELECT ON TABLE road_insight.vw_state_yoy_comparison TO roadinsight_dashboard;

-- 6. Enforce execution guardrails at the role level
ALTER ROLE roadinsight_dashboard SET default_transaction_read_only = on;
ALTER ROLE roadinsight_dashboard SET statement_timeout = '10000ms';
ALTER ROLE roadinsight_dashboard SET search_path = road_insight, public;

-- 7. Verification output
SELECT rolname, rolsuper, rolcreaterole, rolcreatedb, rolinherit, rolcanlogin 
FROM pg_roles 
WHERE rolname = 'roadinsight_dashboard';

