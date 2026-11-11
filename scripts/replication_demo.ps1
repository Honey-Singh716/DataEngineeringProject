# =======================================================================
# ROAD INSIGHT — Streaming Replication Demonstration Script (PowerShell)
# File: scripts/replication_demo.ps1
# Usage:
#   .\scripts\replication_demo.ps1
# =======================================================================

param(
    [string]$PrimaryHost = "localhost",
    [int]$PrimaryPort = 5432,
    [string]$ReplicaHost = "localhost",
    [int]$ReplicaPort = 5433,
    [string]$Database = "roadinsight",
    [string]$User = "postgres"
)

$ErrorActionPreference = "Stop"

Write-Host "===========================================================" -ForegroundColor Green
Write-Host " ROAD INSIGHT: Testing Primary-Replica Cluster" -ForegroundColor Green
Write-Host " Primary Node : $PrimaryHost:$PrimaryPort"
Write-Host " Replica Node : $ReplicaHost:$ReplicaPort"
Write-Host "==========================================================="

try {
    # 1. Check Primary Role
    Write-Host "[1/3] Verifying Primary Node status..." -ForegroundColor Cyan
    $PrimaryCheck = "SELECT pg_is_in_recovery();" | & psql -h $PrimaryHost -p $PrimaryPort -U $User -d $Database -t -A
    if ($PrimaryCheck -eq "f") {
        Write-Host "  -> Primary Node is in READ-WRITE mode (pg_is_in_recovery = false)" -ForegroundColor Green
    } else {
        throw "Primary node failed recovery check: $PrimaryCheck"
    }

    # 2. Check Replica Role
    Write-Host "[2/3] Verifying Standby Replica Node status..." -ForegroundColor Cyan
    $ReplicaCheck = "SELECT pg_is_in_recovery();" | & psql -h $ReplicaHost -p $ReplicaPort -U $User -d $Database -t -A
    if ($ReplicaCheck -eq "t") {
        Write-Host "  -> Standby Replica Node is in READ-ONLY HOT-STANDBY mode (pg_is_in_recovery = true)" -ForegroundColor Green
    } else {
        throw "Standby replica failed recovery check: $ReplicaCheck"
    }

    # 3. Check Replication Lag
    Write-Host "[3/3] Checking replication stream status..." -ForegroundColor Cyan
    $LagSql = @"
    SELECT client_addr, state, sync_state,
           (pg_wal_lsn_diff(pg_current_wal_lsn(), replay_lsn)) AS byte_lag
    FROM pg_stat_replication;
"@
    $LagResult = $LagSql | & psql -h $PrimaryHost -p $PrimaryPort -U $User -d $Database -t -A -F " | "
    Write-Host "  Replication Streams:" -ForegroundColor Yellow
    foreach ($line in $LagResult) {
        Write-Host "  -> $line bytes lag"
    }

    Write-Host "`n[SUCCESS] Multi-node streaming replication cluster is operational!" -ForegroundColor Green
    exit 0
}
catch {
    Write-Host "[ERROR] Replication demo check failed: $_" -ForegroundColor Red
    exit 1
}

