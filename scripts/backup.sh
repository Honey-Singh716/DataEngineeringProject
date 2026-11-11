#!/usr/bin/env bash
# =======================================================================
# ROAD INSIGHT — Automated Database Backup Script (Bash)
# File: scripts/backup.sh
# =======================================================================
set -euo pipefail

HOST="${1:-localhost}"
PORT="${2:-5432}"
DB="${3:-roadinsight}"
USER="${4:-postgres}"
BACKUP_DIR="${5:-backups}"

mkdir -p "$BACKUP_DIR"
TS=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/${DB}_backup_${TS}.dump"

echo "Starting backup of ${DB} on ${HOST}:${PORT} -> ${BACKUP_FILE}..."
pg_dump -h "$HOST" -p "$PORT" -U "$USER" -d "$DB" --schema=road_insight --schema=public -Fc -f "$BACKUP_FILE"

echo "Backup completed successfully: ${BACKUP_FILE} ($(du -h "$BACKUP_FILE" | cut -f1))"

