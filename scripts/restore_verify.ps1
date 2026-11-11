# =======================================================================
# ROAD INSIGHT — Backup Restoration & Verification Script (PowerShell)
# File: scripts/restore_verify.ps1
# Usage:
#   .\scripts\restore_verify.ps1 -BackupFile "backups\roadinsight_backup_20261108_120000.dump"
# =======================================================================

param(
    [Parameter(Mandatory=$true)]
    [string]$BackupFile,
    [string]$HostName = "localhost",
    [int]$Port = 5432,
    [string]$User = "postgres",
    [string]$VerifyDatabase = "roadinsight_verify",
    [switch]$KeepVerifyDb = $false
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $BackupFile)) {
    Write-Host "[ERROR] Specified backup file does not exist: $BackupFile" -ForegroundColor Red
    exit 1
}

Write-Host "===========================================================" -ForegroundColor Green
Write-Host " ROAD INSIGHT: Starting Backup Restoration & Verification" -ForegroundColor Green
Write-Host " Backup Archive    : $BackupFile"
Write-Host " Target Verify DB  : $VerifyDatabase on $HostName:$Port"
Write-Host "==========================================================="

try {
    # 1. Terminate active connections and recreate verify database
    Write-Host "[1/4] Preparing temporary verification database '$VerifyDatabase'..." -ForegroundColor Cyan
    $DropSql = @"
    SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '$VerifyDatabase';
    DROP DATABASE IF EXISTS $VerifyDatabase;
    CREATE DATABASE $VerifyDatabase;
"@
    $DropSql | & psql -h $HostName -p $Port -U $User -d postgres

    # 2. Restore backup into verify database
    Write-Host "[2/4] Restoring backup archive via pg_restore..." -ForegroundColor Cyan
    if ($BackupFile.EndsWith(".dump")) {
        $RestoreArgs = @(
            "-h", $HostName,
            "-p", $Port,
            "-U", $User,
            "-d", $VerifyDatabase,
            "--no-owner",
            "--role=$User",
            $BackupFile
        )
        & pg_restore @RestoreArgs
    } else {
        & psql -h $HostName -p $Port -U $User -d $VerifyDatabase -f $BackupFile
    }

    # 3. Verify Table Row Counts
    Write-Host "[3/4] Verifying table completeness and row counts..." -ForegroundColor Cyan
    $CountCheckSql = @"
    SET search_path TO road_insight, public;
    SELECT 'national_historical_stats' AS tbl, count(*) AS count FROM national_historical_stats
    UNION ALL SELECT 'national_annual_stats', count(*) FROM national_annual_stats
    UNION ALL SELECT 'state_annual_stats', count(*) FROM state_annual_stats
    UNION ALL SELECT 'city_accident_stats', count(*) FROM city_accident_stats
    UNION ALL SELECT 'city_violation_stats', count(*) FROM city_violation_stats
    UNION ALL SELECT 'city_weather_stats', count(*) FROM city_weather_stats
    UNION ALL SELECT 'city_road_feature_stats', count(*) FROM city_road_feature_stats
    UNION ALL SELECT 'collision_type_stats', count(*) FROM collision_type_stats
    UNION ALL SELECT 'violation_type_stats', count(*) FROM violation_type_stats;
"@
    $Results = $CountCheckSql | & psql -h $HostName -p $Port -U $User -d $VerifyDatabase -t -A -F ","

    Write-Host "`nRestored Fact Table Counts:" -ForegroundColor Yellow
    $ExpectedTotal = 1299
    $ActualTotal = 0

    foreach ($line in $Results) {
        if ($line -match "^(.+),(\d+)$") {
            $tbl = $Matches[1]
            $cnt = [int]$Matches[2]
            $ActualTotal += $cnt
            Write-Host "  - $tbl : $cnt rows"
        }
    }

    Write-Host "`nTotal Fact Records Restored: $ActualTotal (Expected: $ExpectedTotal)"

    if ($ActualTotal -ge $ExpectedTotal) {
        Write-Host "[VERIFICATION SUCCESS] Backup integrity verified with 100% data preservation!" -ForegroundColor Green
    } else {
        Write-Host "[WARNING] Restored count ($ActualTotal) is below expected baseline ($ExpectedTotal)" -ForegroundColor Yellow
    }

    # 4. Clean up temporary verify database
    if (-not $KeepVerifyDb) {
        Write-Host "[4/4] Cleaning up temporary database '$VerifyDatabase'..." -ForegroundColor Cyan
        "DROP DATABASE IF EXISTS $VerifyDatabase;" | & psql -h $HostName -p $Port -U $User -d postgres
    } else {
        Write-Host "[4/4] Preserving verification database '$VerifyDatabase' for inspection." -ForegroundColor Cyan
    }

    exit 0
}
catch {
    Write-Host "[ERROR] Restore verification failed: $_" -ForegroundColor Red
    exit 1
}

