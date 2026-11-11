<#
.SYNOPSIS
    Automated local setup for Road Insight database and ETL pipeline on Windows.
.DESCRIPTION
    Initializes PostgreSQL schema, tables, constraints, indexes, reference data,
    runs the python ETL loader, sets up views, and creates application roles.
    Never hardcodes passwords; reads from environment or prompts securely.
.EXAMPLE
    .\scripts\setup_local.ps1
#>

[CmdletBinding()]
param(
    [string]$PgHost = "localhost",
    [int]$PgPort = 5432,
    [string]$PgDatabase = "roadinsight",
    [string]$PgUser = "postgres"
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot

Write-Host "====================================================" -ForegroundColor Cyan
Write-Host "  Road Insight India: Local Database Setup (Windows)" -ForegroundColor Cyan
Write-Host "====================================================" -ForegroundColor Cyan

# 1. Resolve Admin Password
$adminPass = $env:PGPASSWORD
if ([string]::IsNullOrWhiteSpace($adminPass)) {
    $adminPass = $env:POSTGRES_PASSWORD
}
if ([string]::IsNullOrWhiteSpace($adminPass)) {
    $secPass = Read-Host -Prompt "Enter PostgreSQL password for user '$PgUser'" -AsSecureString
    $BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($secPass)
    $adminPass = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)
}
$env:PGPASSWORD = $adminPass

# Helper function to run psql
function Run-Psql {
    param(
        [string]$File,
        [string]$Db = $PgDatabase,
        [hashtable]$Variables = @{}
    )
    $argsList = @(
        "-h", $PgHost,
        "-p", $PgPort.ToString(),
        "-U", $PgUser,
        "-d", $Db,
        "-v", "ON_ERROR_STOP=1"
    )
    foreach ($k in $Variables.Keys) {
        $argsList += "-v"
        $argsList += "$k=$($Variables[$k])"
    }
    if ($File) {
        $argsList += "-f"
        $argsList += $File
    }

    $proc = Start-Process -FilePath "psql" -ArgumentList $argsList -NoNewWindow -Wait -PassThru
    if ($proc.ExitCode -ne 0) {
        throw "psql failed for file $File with exit code $($proc.ExitCode)"
    }
}

try {
    Write-Host "`n[1/7] Ensuring database '$PgDatabase' exists..." -ForegroundColor Yellow
    # Check if database exists
    $checkDb = & psql -h $PgHost -p $PgPort -U $PgUser -d "postgres" -tAc "SELECT 1 FROM pg_database WHERE datname='$PgDatabase'" 2>$null
    if ($checkDb -ne "1") {
        Write-Host "Creating database '$PgDatabase'..."
        & psql -h $PgHost -p $PgPort -U $PgUser -d "postgres" -c "CREATE DATABASE $PgDatabase;"
    } else {
        Write-Host "Database '$PgDatabase' already exists."
    }

    Write-Host "`n[2/7] Creating schema and core objects (01..05)..." -ForegroundColor Yellow
    Run-Psql -File (Join-Path $ProjectRoot "db_design\sql\01_create_schema.sql")
    Run-Psql -File (Join-Path $ProjectRoot "db_design\sql\02_create_tables.sql")
    Run-Psql -File (Join-Path $ProjectRoot "db_design\sql\03_create_constraints.sql")
    Run-Psql -File (Join-Path $ProjectRoot "db_design\sql\04_create_indexes.sql")
    Run-Psql -File (Join-Path $ProjectRoot "db_design\sql\05_insert_reference_data.sql")

    Write-Host "`n[3/7] Running Python ETL Loader (06_etl_loader.py)..." -ForegroundColor Yellow
    $connUri = "postgresql://${PgUser}:${adminPass}@${PgHost}:${PgPort}/${PgDatabase}"
    $etlScript = Join-Path $ProjectRoot "db_design\06_etl_loader.py"
    $etlProc = Start-Process -FilePath "python" -ArgumentList @($etlScript, "--conn", $connUri) -NoNewWindow -Wait -PassThru
    if ($etlProc.ExitCode -ne 0) {
        throw "ETL loader failed with exit code $($etlProc.ExitCode)"
    }

    Write-Host "`n[4/7] Creating Analytical Views (08_views.sql)..." -ForegroundColor Yellow
    Run-Psql -File (Join-Path $ProjectRoot "db_design\sql\08_views.sql")

    Write-Host "`n[5/7] Setting up application roles..." -ForegroundColor Yellow
    $roScript = Join-Path $ProjectRoot "scripts\setup_readonly_role.sql"
    if (Test-Path $roScript) {
        Run-Psql -File $roScript
    }

    Write-Host "`n[6/7] Validating row counts and integrity (07_validation_queries.sql)..." -ForegroundColor Yellow
    $valScript = Join-Path $ProjectRoot "db_design\sql\07_validation_queries.sql"
    Run-Psql -File $valScript

    Write-Host "`n[7/7] Database setup and ETL complete successfully!" -ForegroundColor Green
}
catch {
    Write-Error "Setup failed: $_"
    exit 1
}
finally {
    $env:PGPASSWORD = $null
}
