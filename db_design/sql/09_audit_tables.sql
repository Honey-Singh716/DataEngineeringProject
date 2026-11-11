-- =============================================================
-- ROAD INSIGHT: Audit and Data Quality Tables
-- File: db_design/sql/09_audit_tables.sql
-- Purpose: Schema definitions for ETL run tracking, row rejections,
--          and data quality validation check results.
-- =============================================================

SET search_path TO road_insight, public;

-- 1. ETL Run Master Log
CREATE TABLE IF NOT EXISTS road_insight.etl_run_log (
    run_id          BIGSERIAL PRIMARY KEY,
    started_at      TIMESTAMPTZ NOT NULL DEFAULT CLOCK_TIMESTAMP(),
    finished_at     TIMESTAMPTZ,
    status          VARCHAR(32) NOT NULL DEFAULT 'STARTED',
    rows_read       INTEGER DEFAULT 0,
    rows_loaded     INTEGER DEFAULT 0,
    rows_rejected   INTEGER DEFAULT 0,
    null_coerced    INTEGER DEFAULT 0,
    git_commit      VARCHAR(64),
    host            VARCHAR(128)
);

-- 2. Per-Table Detail Run Log
CREATE TABLE IF NOT EXISTS road_insight.etl_run_table_log (
    log_id          BIGSERIAL PRIMARY KEY,
    run_id          BIGINT NOT NULL REFERENCES road_insight.etl_run_log(run_id) ON DELETE CASCADE,
    table_name      VARCHAR(128) NOT NULL,
    rows_read       INTEGER DEFAULT 0,
    rows_loaded     INTEGER DEFAULT 0,
    rows_rejected   INTEGER DEFAULT 0,
    seconds         NUMERIC(10,3) DEFAULT 0.000
);

-- 3. Rejected / Skipped Rows Audit Log
CREATE TABLE IF NOT EXISTS road_insight.rejected_rows (
    rejection_id    BIGSERIAL PRIMARY KEY,
    run_id          BIGINT,
    source_file     VARCHAR(255) NOT NULL,
    row_number      INTEGER,
    reason          TEXT NOT NULL,
    raw_row         JSONB,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT CLOCK_TIMESTAMP()
);

-- 4. Data Quality Check Results (Framework results store)
CREATE TABLE IF NOT EXISTS road_insight.dq_check_results (
    result_id       BIGSERIAL PRIMARY KEY,
    run_id          BIGINT,
    check_id        VARCHAR(32) NOT NULL,
    check_name      TEXT NOT NULL,
    table_name      VARCHAR(128),
    severity        VARCHAR(16) NOT NULL DEFAULT 'FAIL',
    rows_checked    INTEGER DEFAULT 0,
    rows_failed     INTEGER DEFAULT 0,
    status          VARCHAR(16) NOT NULL DEFAULT 'PASS',
    detail          TEXT,
    checked_at      TIMESTAMPTZ NOT NULL DEFAULT CLOCK_TIMESTAMP()
);

-- Create indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_etl_run_status ON road_insight.etl_run_log(status);
CREATE INDEX IF NOT EXISTS idx_etl_table_run ON road_insight.etl_run_table_log(run_id, table_name);
CREATE INDEX IF NOT EXISTS idx_rejected_rows_run ON road_insight.rejected_rows(run_id, source_file);
CREATE INDEX IF NOT EXISTS idx_dq_check_run ON road_insight.dq_check_results(run_id, check_id);

-- Grants: allow dashboard and readonly roles to read audit data
GRANT SELECT ON TABLE road_insight.etl_run_log TO roadinsight_dashboard, roadinsight_readonly;
GRANT SELECT ON TABLE road_insight.etl_run_table_log TO roadinsight_dashboard, roadinsight_readonly;
GRANT SELECT ON TABLE road_insight.rejected_rows TO roadinsight_dashboard, roadinsight_readonly;
GRANT SELECT ON TABLE road_insight.dq_check_results TO roadinsight_dashboard, roadinsight_readonly;

