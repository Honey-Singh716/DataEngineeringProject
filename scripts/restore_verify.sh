#!/usr/bin/env bash
# =======================================================================
# ROAD INSIGHT — Backup Restoration & Verification Script (Bash)
# File: scripts/restore_verify.sh
# =======================================================================
set -euo pipefail

BACKUP_FILE="${1:-}"
if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <path_to_backup.dump> [host] [port] [user] [verify_db]"
    exit 1
fi

HOST="${2:-localhost}"
PORT="${3:-5432}"
USER="${4:-postgres}"
VERIFY_DB="${5:-roadinsight_verify}"

echo "Preparing verification database: ${VERIFY_DB} on ${HOST}:${PORT}..."
psql -h "$HOST" -p "$PORT" -U "$USER" -d postgres -c "DROP DATABASE IF EXISTS ${VERIFY_DB}; CREATE DATABASE ${VERIFY_DB};"

echo "Restoring ${BACKUP_FILE} into ${VERIFY_DB}..."
pg_restore -h "$HOST" -p "$PORT" -U "$USER" -d "$VERIFY_DB" --no-owner "$BACKUP_FILE"

echo "Verifying row counts in ${VERIFY_DB}..."
COUNT_SQL="
SET search_path TO road_insight, public;
SELECT 'national_historical_stats', count(*) FROM national_historical_stats
UNION ALL SELECT 'national_annual_stats', count(*) FROM national_annual_stats
UNION ALL SELECT 'state_annual_stats', count(*) FROM state_annual_stats
UNION ALL SELECT 'city_accident_stats', count(*) FROM city_accident_stats
UNION ALL SELECT 'city_violation_stats', count(*) FROM city_violation_stats
UNION ALL SELECT 'city_weather_stats', count(*) FROM city_weather_stats
UNION ALL SELECT 'city_road_feature_stats', count(*) FROM city_road_feature_stats
UNION ALL SELECT 'collision_type_stats', count(*) FROM collision_type_stats
UNION ALL SELECT 'violation_type_stats', count(*) FROM violation_type_stats;
"
psql -h "$HOST" -p "$PORT" -U "$USER" -d "$VERIFY_DB" -t -A -F " : " -c "$COUNT_SQL"

echo "Dropping temporary verification database: ${VERIFY_DB}..."
psql -h "$HOST" -p "$PORT" -U "$USER" -d postgres -c "DROP DATABASE IF EXISTS ${VERIFY_DB};"
echo "Restore verification completed successfully!"
