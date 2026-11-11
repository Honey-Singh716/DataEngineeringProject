# =======================================================================
# ROAD INSIGHT — Automated Database Backup Script (PowerShell)
# File: scripts/backup.ps1
# Usage:
#   .\scripts\backup.ps1 -Host "localhost" -Port 5432 -Database "roadinsight" -User "postgres" -BackupDir "backups"
# =======================================================================

param(
    [string]$HostName = "localhost",
    [int]$Port = 5432,
    [string]$Database = "roadinsight",
    [string]$User = "postgres",
    [string]$BackupDir = "backups",
    [ValidateSet("custom", "plain")][string]$Format = "custom"
)

$ErrorActionPreference = "Stop"

# Ensure backup directory exists
if (-not (Test-Path -Path $BackupDir)) {
    New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null
    Write-Host "[INFO] Created backup directory: $BackupDir" -ForegroundColor Cyan
}

$Timestamp = (Get-Date).ToString("yyyyMMdd_HHmmss")
if ($Format -eq "custom") {
    $BackupFile = Join-Path $BackupDir "${Database}_backup_${Timestamp}.dump"
    $FormatFlag = "-Fc"
} else {
    $BackupFile = Join-Path $BackupDir "${Database}_backup_${Timestamp}.sql"
    $FormatFlag = "-Fp"
}

Write-Host "===========================================================" -ForegroundColor Green
Write-Host " ROAD INSIGHT: Starting Database Backup" -ForegroundColor Green
Write-Host " Target Database : $Database ($HostName:$Port)"
Write-Host " Destination File: $BackupFile"
Write-Host "==========================================================="

$Stopwatch = [System.Diagnostics.Stopwatch]::StartNew()

try {
    # Check if pg_dump is available
    if (-not (Get-Command "pg_dump" -ErrorAction SilentlyContinue)) {
        throw "pg_dump command not found in PATH. Please install PostgreSQL client tools or add bin directory to PATH."
    }

    $DumpArgs = @(
        "-h", $HostName,
        "-p", $Port,
        "-U", $User,
        "-d", $Database,
        "--schema=road_insight",
        "--schema=public",
        "--verbose",
        $FormatFlag,
        "-f", $BackupFile
    )

    & pg_dump @DumpArgs
    $Stopwatch.Stop()

    if ($LASTEXITCODE -eq 0 -and (Test-Path $BackupFile)) {
        $FileSizeMB = [Math]::Round((Get-Item $BackupFile).Length / 1MB, 2)
        Write-Host "[SUCCESS] Backup completed successfully in $($Stopwatch.Elapsed.TotalSeconds.ToString('F2'))s" -ForegroundColor Green
        Write-Host " Backup Archive: $BackupFile ($FileSizeMB MB)" -ForegroundColor Yellow
        exit 0
    } else {
        throw "pg_dump exited with error code: $LASTEXITCODE"
    }
}
catch {
    $Stopwatch.Stop()
    Write-Host "[ERROR] Backup failed: $_" -ForegroundColor Red
    exit 1
}
