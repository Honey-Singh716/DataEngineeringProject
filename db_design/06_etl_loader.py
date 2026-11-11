#!/usr/bin/env python3
"""
ROAD INSIGHT — Hardened ETL Data Loader
File: db_design/06_etl_loader.py

Transforms raw CSV files -> cleaned -> PostgreSQL (road_insight schema).

Key Features:
1. Atomicity: The entire load executes in a single transaction. If any table
   fails, all changes are rolled back.
2. Idempotency: Running repeatedly replaces existing facts cleanly without duplicates.
3. Named Columns: Positional lookups (e.g., iloc[2, 4, 6]) are completely eliminated.
4. Rejection Tracking: Non-integer decimals, invalid numbers, and unresolvable entities
   are captured into road_insight.rejected_rows with full audit context.
5. Audit Run Logging: Master run metrics (road_insight.etl_run_log) and per-table timings
   (road_insight.etl_run_table_log) are recorded automatically.
6. Validation Against Expected Counts: Compares row counts against expectations from
   db_design/sql/07_validation_queries.sql.
7. Multi-Mode Support: Supports --conn for live DB runs and --dry-run for offline verification.
"""

import os
import sys
import re
import json
import time
import socket
import logging
import argparse
import subprocess
from pathlib import Path
from datetime import datetime, timezone
import pandas as pd
import numpy as np

try:
    from sqlalchemy import create_engine, text
except ImportError:
    create_engine = None
    text = None

SCHEMA = 'road_insight'

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / 'Data'
DATASETS_DIR = BASE_DIR / 'DataSets'

# City name mapping: raw source name -> canonical DB name
CITY_NAME_MAP = {
    'allahabad (prayagraj)':   'Allahabad (Prayagraj)',
    'allahabad(prayagraj)':    'Allahabad (Prayagraj)',
    'khozikode':               'Kozhikode',
    'mallapuram':              'Malappuram',
    'thiruvanthapuram':        'Thiruvananthapuram',
    'thiruvananthapuram':      'Thiruvananthapuram',
    'vijaywada city':          'Vijayawada',
    'vizaq':                   'Visakhapatnam',
    'vadodra':                 'Vadodara',
}

# State name mapping: raw source name -> canonical DB name
STATE_NAME_MAP = {
    'j & k #':  'Jammu & Kashmir',
    'j & k':    'Jammu & Kashmir',
    'dadra & nagar haveli*': 'Dadra & Nagar Haveli and Daman & Diu',
}

# Static fallbacks for dry-run verification
FALLBACK_DATA_SOURCES = {
    'LargeCities.csv': 1,
    'LargeCitiesVio.csv': 2,
    'RoadNoAcc.csv': 3,
    'RoadStateWiseAcc.csv': 4,
    'RoadStatewiseKilled.csv': 5,
    'RoadTypeColl.csv': 6,
    'RoadTypeViol.csv': 7,
    'RA2019_A1.csv': 8,
    'RA2019_A45.csv': 9,
    'RA2019_A48.csv': 10,
}

EXPECTED_COUNTS = {
    'national_historical_stats': 29,
    'national_annual_stats': 5,
    'state_annual_stats': 185,
    'city_accident_stats': 100,
    'city_violation_stats': 300,
    'city_weather_stats': 250,
    'city_road_feature_stats': 400,
    'collision_type_stats': 18,
    'violation_type_stats': 12,
}

log = logging.getLogger('etl_loader')


# ================================================================
# TRACKER & AUDIT STRUCTURES
# ================================================================

class ETLTracker:
    """Collects audit metrics and row rejections across all loaders."""
    def __init__(self, run_id: int | None = None):
        self.run_id = run_id
        self.rows_read = 0
        self.rows_loaded = 0
        self.rows_rejected = 0
        self.null_coerced = 0
        self.rejected_rows: list[dict] = []
        self.table_logs: list[dict] = []

    def increment_read(self, n: int = 1):
        self.rows_read += n

    def increment_loaded(self, n: int = 1):
        self.rows_loaded += n

    def increment_null(self, n: int = 1):
        self.null_coerced += n

    def record_rejection(self, source_file: str, row_number: int | None, reason: str, raw_row=None):
        self.rows_rejected += 1
        clean_raw = None
        if raw_row is not None:
            if isinstance(raw_row, pd.Series):
                clean_raw = {k: v for k, v in raw_row.dropna().to_dict().items()}
            elif isinstance(raw_row, dict):
                clean_raw = {k: v for k, v in raw_row.items() if pd.notna(v)}
            else:
                clean_raw = str(raw_row)
        self.rejected_rows.append({
            'run_id': self.run_id,
            'source_file': str(source_file),
            'row_number': int(row_number) if row_number is not None else None,
            'reason': str(reason),
            'raw_row': json.dumps(clean_raw, default=str) if clean_raw is not None else None
        })

    def record_table_log(self, table_name: str, rows_read: int, rows_loaded: int, rows_rejected: int, seconds: float):
        self.table_logs.append({
            'run_id': self.run_id,
            'table_name': table_name,
            'rows_read': rows_read,
            'rows_loaded': rows_loaded,
            'rows_rejected': rows_rejected,
            'seconds': round(seconds, 3)
        })


def get_git_commit() -> str:
    """Retrieve current git commit hash."""
    try:
        res = subprocess.run(['git', 'rev-parse', 'HEAD'], capture_output=True, text=True, timeout=5, cwd=str(BASE_DIR))
        if res.returncode == 0:
            return res.stdout.strip()[:40]
    except Exception:
        pass
    return 'unknown'


def get_hostname() -> str:
    """Retrieve system hostname."""
    try:
        return socket.gethostname()[:128]
    except Exception:
        return 'unknown'


# ================================================================
# UTILITY FUNCTIONS
# ================================================================

def parse_indian_number(val, tracker: ETLTracker | None = None,
                        source_file: str = 'unknown', row_num: int | None = None,
                        raw_row=None, field_name: str = 'unknown') -> int | None:
    """
    Parse Indian comma-formatted numbers like '4,56,959' -> 456959.
    - NA-like strings ('NA', 'N/A', '-', '', None) are coerced to None and increment null_coerced.
    - Non-integer decimals (e.g. '12.7') are rejected to rejected_rows with reason 'non_integer_value'.
    - Valid integers (e.g. 12, '12', '12.0', '4,56,959') are returned as int.
    """
    if pd.isna(val):
        if tracker:
            tracker.increment_null()
        return None

    s = str(val).strip()
    if s in ('NA', 'N/A', '#N/A', 'Na', '', '-', '--'):
        if tracker:
            tracker.increment_null()
        return None

    s = s.replace(',', '')
    try:
        f = float(s)
        if f.is_integer():
            return int(f)
        else:
            if tracker:
                tracker.record_rejection(
                    source_file=source_file,
                    row_number=row_num,
                    reason=f"non_integer_value: '{val}' in {field_name}",
                    raw_row=raw_row
                )
            return None
    except (ValueError, TypeError):
        if tracker:
            tracker.record_rejection(
                source_file=source_file,
                row_number=row_num,
                reason=f"invalid_number_format: '{val}' in {field_name}",
                raw_row=raw_row
            )
        return None


def parse_float_nullable(val, tracker: ETLTracker | None = None) -> float | None:
    """Parse float; return None for NA-like strings."""
    if pd.isna(val):
        if tracker:
            tracker.increment_null()
        return None
    s = str(val).strip()
    if s in ('NA', 'N/A', '#N/A', 'Na', '', '-', '--'):
        if tracker:
            tracker.increment_null()
        return None
    s = s.replace(',', '')
    try:
        return float(s)
    except (ValueError, TypeError):
        return None


def normalize_city_name(raw: str) -> str:
    """Apply canonical city name mapping."""
    if pd.isna(raw):
        return raw
    key = str(raw).strip().lower()
    return CITY_NAME_MAP.get(key, str(raw).strip())


def normalize_state_name(raw: str) -> str:
    """Apply canonical state name mapping."""
    if pd.isna(raw):
        return raw
    key = str(raw).strip().lower()
    return STATE_NAME_MAP.get(key, str(raw).strip())


def get_lookup(conn, table: str, name_col: str, id_col: str) -> dict:
    """Load a reference table into a name -> id dict. Uses static fallback in dry-run/mock mode."""
    if conn is not None and text is not None:
        rows = conn.execute(text(
            f'SELECT {name_col}, {id_col} FROM {SCHEMA}.{table}'
        )).fetchall()
        return {row[0]: row[1] for row in rows}

    # Static fallback for dry-run
    if table == 'states':
        states = [
            'Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chhattisgarh',
            'Goa', 'Gujarat', 'Haryana', 'Himachal Pradesh', 'Jharkhand',
            'Karnataka', 'Kerala', 'Madhya Pradesh', 'Maharashtra', 'Manipur',
            'Meghalaya', 'Mizoram', 'Nagaland', 'Odisha', 'Punjab',
            'Rajasthan', 'Sikkim', 'Tamil Nadu', 'Telangana', 'Tripura',
            'Uttarakhand', 'Uttar Pradesh', 'West Bengal', 'Andaman & Nicobar Islands',
            'Chandigarh', 'Dadra & Nagar Haveli and Daman & Diu', 'Daman & Diu',
            'Delhi', 'Jammu & Kashmir', 'Ladakh', 'Lakshadweep', 'Puducherry'
        ]
        return {s: i + 1 for i, s in enumerate(states)}
    elif table == 'cities':
        cities = [
            'Agra', 'Ahmedabad', 'Allahabad (Prayagraj)', 'Amritsar', 'Asansol Durgapur',
            'Aurangabad', 'Bengaluru', 'Bhopal', 'Chandigarh', 'Coimbatore',
            'Chennai', 'Delhi', 'Dhanbad', 'Faridabad', 'Ghaziabad',
            'Gwalior', 'Hyderabad', 'Indore', 'Jabalpur', 'Jaipur',
            'Jamshedpur', 'Jodhpur', 'Kannur', 'Kanpur', 'Kozhikode',
            'Kochi', 'Kolkata', 'Kollam', 'Kota', 'Lucknow',
            'Ludhiana', 'Madurai', 'Malappuram', 'Meerut', 'Mumbai',
            'Nagpur', 'Nashik', 'Patna', 'Pune', 'Raipur',
            'Rajkot', 'Srinagar', 'Surat', 'Thiruvananthapuram', 'Thrissur',
            'Tiruchirapalli', 'Vadodara', 'Varanasi', 'Vijayawada', 'Visakhapatnam'
        ]
        return {c: i + 1 for i, c in enumerate(cities)}
    elif table == 'weather_conditions':
        weathers = ['Sunny/Clear', 'Rainy', 'Foggy and Misty', 'Hail/Sleet', 'Others']
        return {w: i + 1 for i, w in enumerate(weathers)}
    elif table == 'road_features':
        rfs = ['Straight Road', 'Curved Road', 'Bridge', 'Culvert', 'Pot Holes',
               'Steep Grade', 'Ongoing Road Works/Under Construction', 'Others']
        return {r: i + 1 for i, r in enumerate(rfs)}
    elif table == 'collision_types':
        cts = ['Hit and Run', 'With parked Vehicle', 'Hit from Back', 'Hit from side',
               'Run off Road', 'Fixed object', 'Vehicle overturn', 'Head on collision', 'Others']
        return {c: i + 1 for i, c in enumerate(cts)}
    elif table == 'violation_types':
        vts = ['Over-speeding', 'Drunken driving/consumption of alcohol & drug',
               'Driving on wrong side/Lane indiscipline', 'Jumping red light',
               'Use of mobile phone', 'Others']
        return {v: i + 1 for i, v in enumerate(vts)}
    return {}


def get_source_id(conn, source_file: str) -> int:
    """Lookup source_id by file name."""
    if conn is not None and text is not None:
        row = conn.execute(text(
            f"SELECT source_id FROM {SCHEMA}.data_sources WHERE source_file = :f"
        ), {'f': source_file}).fetchone()
        if row is not None:
            return row[0]
        raise ValueError(f"source_file '{source_file}' not found in data_sources table. "
                         "Run 05_insert_reference_data.sql first.")
    return FALLBACK_DATA_SOURCES.get(source_file, 1)


# ================================================================
# LOADERS
# ================================================================

def load_ra2019_a1(conn, tracker: ETLTracker) -> pd.DataFrame:
    """Load DataSets/RA2019_A1.csv -> national_historical_stats."""
    source_file = 'RA2019_A1.csv'
    log.info(f"Loading {source_file} -> national_historical_stats")
    source_id = get_source_id(conn, source_file)

    csv_path = DATASETS_DIR / source_file
    df_raw = pd.read_csv(csv_path)
    tracker.increment_read(len(df_raw))

    # Rename columns (strip whitespace, duplicate spaces)
    df = df_raw.copy()
    df.columns = [re.sub(r'\s+', ' ', c).strip() for c in df.columns]

    # Filter out CAGR and empty rows
    cagr_mask = df['Years'].astype(str).str.contains('CAGR', na=False)
    for idx, r in df[cagr_mask].iterrows():
        tracker.record_rejection(source_file, idx + 2, "excluded_summary_cagr_row", r)

    df = df[~cagr_mask].copy()
    df = df[df['Years'].notna()].copy()

    records = []
    for idx, row in df.iterrows():
        row_num = idx + 2  # 1-based + 1 header
        year_val = parse_indian_number(row['Years'], tracker, source_file, row_num, row, 'Years')
        if year_val is None:
            tracker.record_rejection(source_file, row_num, "missing_or_invalid_year", row)
            continue

        records.append({
            'year':                           year_val,
            'source_id':                      source_id,
            'total_accidents':                parse_indian_number(row.get('Total Number of Road Accidents (in numbers)'), tracker, source_file, row_num, row, 'total_accidents'),
            'total_killed':                   parse_indian_number(row.get('Total Number of Persons Killed (in numbers)'), tracker, source_file, row_num, row, 'total_killed'),
            'total_injured':                  parse_indian_number(row.get('Total Number of Persons Injured (in numbers)'), tracker, source_file, row_num, row, 'total_injured'),
            'population_thousands':           parse_float_nullable(row.get('Population of India (in thousands)'), tracker),
            'registered_vehicles_thousands':  parse_float_nullable(row.get('Total Number of Registered Motor Vehicles (in thousands)'), tracker),
            'road_length_km':                 parse_float_nullable(row.get('Road Length (in kms)'), tracker),
            'accidents_per_lakh_pop':         parse_float_nullable(row.get('Number of Accidents per Lakh Population'), tracker),
            'accidents_per_10k_vehicles':     parse_float_nullable(row.get('Number of Accidents per Ten Thousand Vehicles'), tracker),
            'accidents_per_10k_km_roads':     parse_float_nullable(row.get('Number of Accidents per Ten Thousand Kms of Roads'), tracker),
            'killed_per_lakh_pop':            parse_float_nullable(row.get('Number of Persons Killed Per Lakh Population'), tracker),
            'killed_per_10k_vehicles':        parse_float_nullable(row.get('Number of Persons Killed Per Ten Thousand Vehicles'), tracker),
            'killed_per_10k_km_roads':        parse_float_nullable(row.get('Number of Persons Killed per Ten Thousand Kms of Roads'), tracker),
            'injured_per_lakh_pop':           parse_float_nullable(row.get('Number of Persons Injured per Lakh Population'), tracker),
            'injured_per_10k_vehicles':       parse_float_nullable(row.get('Number of Persons Injured Per Ten Thousand Vehicles'), tracker),
            'injured_per_10k_km_roads':       parse_float_nullable(row.get('Number of Persons Injured Per Ten Thousand Kms of Roads'), tracker),
        })

    out = pd.DataFrame(records)
    if conn is not None:
        conn.execute(text(f'DELETE FROM {SCHEMA}.national_historical_stats'))
        out.to_sql('national_historical_stats', conn, schema=SCHEMA,
                   if_exists='append', index=False, method='multi')
    tracker.increment_loaded(len(out))
    log.info(f"  national_historical_stats: read {len(df_raw)}, loaded {len(out)}")
    return out


def load_road_no_acc(conn, tracker: ETLTracker) -> pd.DataFrame:
    """
    Load Data/RoadNoAcc.csv -> national_annual_stats.
    Uses explicit column names instead of positional iloc[2, 4, 6].
    """
    source_file = 'RoadNoAcc.csv'
    log.info(f"Loading {source_file} -> national_annual_stats")
    source_id = get_source_id(conn, source_file)

    csv_path = DATA_DIR / source_file
    df_raw = pd.read_csv(csv_path)
    tracker.increment_read(len(df_raw))

    # Strip column names
    df = df_raw.copy()
    df.columns = [c.strip() for c in df.columns]
    df = df.dropna(subset=['Year'])

    # Explicit column name references for percentage change columns
    # Pandas assigns .1 and .2 to repeated column names
    col_acc_pct = '% Change from previous year'
    col_fat_pct = '% Change from previous year.1' if '% Change from previous year.1' in df.columns else '% Change from previous year'
    col_inj_pct = '% Change from previous year.2' if '% Change from previous year.2' in df.columns else '% Change from previous year'

    records = []
    for idx, row in df.iterrows():
        row_num = idx + 2
        year_val = parse_indian_number(row['Year'], tracker, source_file, row_num, row, 'Year')
        if year_val is None:
            tracker.record_rejection(source_file, row_num, "missing_or_invalid_year", row)
            continue

        records.append({
            'year':                  year_val,
            'source_id':             source_id,
            'total_accidents':       parse_indian_number(row.get('Accidents'), tracker, source_file, row_num, row, 'Accidents'),
            'total_fatalities':      parse_indian_number(row.get('Fatalities'), tracker, source_file, row_num, row, 'Fatalities'),
            'total_injured':         parse_indian_number(row.get('Persons Injured'), tracker, source_file, row_num, row, 'Persons Injured'),
            'accidents_pct_change':  parse_float_nullable(row.get(col_acc_pct), tracker),
            'fatalities_pct_change': parse_float_nullable(row.get(col_fat_pct), tracker),
            'injured_pct_change':    parse_float_nullable(row.get(col_inj_pct), tracker),
        })

    out = pd.DataFrame(records)
    if conn is not None:
        conn.execute(text(f'DELETE FROM {SCHEMA}.national_annual_stats'))
        out.to_sql('national_annual_stats', conn, schema=SCHEMA,
                   if_exists='append', index=False, method='multi')
    tracker.increment_loaded(len(out))
    log.info(f"  national_annual_stats: read {len(df_raw)}, loaded {len(out)}")
    return out


def load_state_stats(conn, tracker: ETLTracker) -> pd.DataFrame:
    """Load RoadStateWiseAcc.csv + RoadStatewiseKilled.csv -> state_annual_stats."""
    source_acc_file = 'RoadStateWiseAcc.csv'
    source_kil_file = 'RoadStatewiseKilled.csv'
    log.info(f"Loading {source_acc_file} + {source_kil_file} -> state_annual_stats")
    source_acc_id = get_source_id(conn, source_acc_file)
    state_lookup = get_lookup(conn, 'states', 'state_name', 'state_id')

    years = [2019, 2020, 2021, 2022, 2023]

    df_acc_raw = pd.read_csv(DATA_DIR / source_acc_file)
    df_kil_raw = pd.read_csv(DATA_DIR / source_kil_file)
    tracker.increment_read(len(df_acc_raw) + len(df_kil_raw))

    mask_acc = (
        df_acc_raw['State'].notna() &
        ~df_acc_raw['State'].astype(str).str.strip().isin(['All India']) &
        ~df_acc_raw['State'].astype(str).str.startswith('#') &
        ~df_acc_raw['State'].astype(str).str.startswith('*')
    )
    df_acc = df_acc_raw[mask_acc].copy()
    df_acc['State'] = df_acc['State'].apply(normalize_state_name)

    mask_kil = (
        df_kil_raw['State'].notna() &
        ~df_kil_raw['State'].astype(str).str.strip().isin(['All India']) &
        ~df_kil_raw['State'].astype(str).str.startswith('#') &
        ~df_kil_raw['State'].astype(str).str.startswith('*')
    )
    df_kil = df_kil_raw[mask_kil].copy()
    df_kil['State'] = df_kil['State'].apply(normalize_state_name)

    records = []
    for idx, row_acc in df_acc.iterrows():
        state_name = row_acc['State']
        state_id = state_lookup.get(state_name)
        row_num = idx + 2
        if state_id is None:
            tracker.record_rejection(source_acc_file, row_num, f"state_not_found_in_reference: '{state_name}'", row_acc)
            continue

        row_kil = df_kil[df_kil['State'] == state_name]

        for yr in years:
            acc_col   = f'{yr} Accidents'
            rank_col  = f'{yr} Ranking'
            kil_col   = f'{yr} Killed'
            krank_col = f'{yr} Ranking'

            acc_count = parse_indian_number(row_acc.get(acc_col), tracker, source_acc_file, row_num, row_acc, acc_col)
            acc_rank  = parse_indian_number(row_acc.get(rank_col), tracker, source_acc_file, row_num, row_acc, rank_col)
            if acc_rank is not None and (acc_rank < 1 or acc_rank > 50):
                acc_rank = None

            killed = None
            kr     = None
            if len(row_kil) > 0:
                kil_series = row_kil.iloc[0]
                killed = parse_indian_number(kil_series.get(kil_col), tracker, source_kil_file, row_num, kil_series, kil_col)
                kr     = parse_indian_number(kil_series.get(krank_col), tracker, source_kil_file, row_num, kil_series, krank_col)
                if kr is not None and (kr < 1 or kr > 50):
                    kr = None

            records.append({
                'state_id':      state_id,
                'year':          yr,
                'source_id':     source_acc_id,
                'accident_count': acc_count,
                'accident_rank':  acc_rank,
                'persons_killed': killed,
                'killed_rank':    kr,
            })

    out = pd.DataFrame(records)
    if conn is not None:
        conn.execute(text(f'DELETE FROM {SCHEMA}.state_annual_stats'))
        out.to_sql('state_annual_stats', conn, schema=SCHEMA,
                   if_exists='append', index=False, method='multi')
    tracker.increment_loaded(len(out))
    log.info(f"  state_annual_stats: read {len(df_acc_raw) + len(df_kil_raw)}, loaded {len(out)}")
    return out


def load_city_accident_stats(conn, tracker: ETLTracker) -> pd.DataFrame:
    """Load Data/LargeCities.csv -> city_accident_stats (unpivoted)."""
    source_file = 'LargeCities.csv'
    log.info(f"Loading {source_file} -> city_accident_stats")
    source_id = get_source_id(conn, source_file)
    city_lookup = get_lookup(conn, 'cities', 'city_name', 'city_id')

    df_raw = pd.read_csv(DATA_DIR / source_file)
    tracker.increment_read(len(df_raw))

    df = df_raw[df_raw['City'].notna() & (df_raw['City'].astype(str).str.strip() != 'Total')].copy()
    df['City'] = df['City'].apply(normalize_city_name)

    records = []
    for idx, row in df.iterrows():
        row_num = idx + 2
        city_name = row['City']
        city_id = city_lookup.get(city_name)
        if city_id is None:
            tracker.record_rejection(source_file, row_num, f"city_not_found_in_reference: '{city_name}'", row)
            continue

        for yr in [2022, 2023]:
            records.append({
                'city_id':        city_id,
                'year':           yr,
                'source_id':      source_id,
                'accident_count': parse_indian_number(row.get(f'{yr} Accidents'), tracker, source_file, row_num, row, f'{yr} Accidents'),
                'persons_killed': parse_indian_number(row.get(f'{yr} Killed'), tracker, source_file, row_num, row, f'{yr} Killed'),
                'persons_injured': parse_indian_number(row.get(f'{yr} Injured'), tracker, source_file, row_num, row, f'{yr} Injured'),
                'accident_rank':  parse_indian_number(row.get(f'{yr} Ranking Accidents'), tracker, source_file, row_num, row, f'{yr} Ranking Accidents'),
                'killed_rank':    parse_indian_number(row.get(f'{yr} Ranking Killed'), tracker, source_file, row_num, row, f'{yr} Ranking Killed'),
                'injured_rank':   parse_indian_number(row.get(f'{yr} Ranking Injured'), tracker, source_file, row_num, row, f'{yr} Ranking Injured'),
            })

    out = pd.DataFrame(records)
    if conn is not None:
        conn.execute(text(f'DELETE FROM {SCHEMA}.city_accident_stats'))
        out.to_sql('city_accident_stats', conn, schema=SCHEMA,
                   if_exists='append', index=False, method='multi')
    tracker.increment_loaded(len(out))
    log.info(f"  city_accident_stats: read {len(df_raw)}, loaded {len(out)}")
    return out


def load_city_violation_stats(conn, tracker: ETLTracker) -> pd.DataFrame:
    """Load Data/LargeCitiesVio.csv -> city_violation_stats (unpivoted)."""
    source_file = 'LargeCitiesVio.csv'
    log.info(f"Loading {source_file} -> city_violation_stats")
    source_id = get_source_id(conn, source_file)
    city_lookup = get_lookup(conn, 'cities', 'city_name', 'city_id')
    vtype_lookup = get_lookup(conn, 'violation_types', 'violation_type_name', 'violation_type_id')

    df_raw = pd.read_csv(DATA_DIR / source_file)
    tracker.increment_read(len(df_raw))

    df = df_raw[df_raw['City'].notna() & (df_raw['City'].astype(str).str.strip() != 'Total')].copy()
    df['City'] = df['City'].apply(normalize_city_name)

    col_to_vtype = {
        'Overspeeding':             'Over-speeding',
        'Drunken Driving/Drugs use':'Drunken driving/consumption of alcohol & drug',
        'Wrong side driving':       'Driving on wrong side/Lane indiscipline',
        'Jumping red light':        'Jumping red light',
        'Using Mobile Phone':       'Use of mobile phone',
        'Others':                   'Others',
    }

    records = []
    for idx, row in df.iterrows():
        row_num = idx + 2
        city_name = row['City']
        city_id = city_lookup.get(city_name)
        if city_id is None:
            tracker.record_rejection(source_file, row_num, f"city_not_found_in_reference: '{city_name}'", row)
            continue

        for col, vtype in col_to_vtype.items():
            vtype_id = vtype_lookup.get(vtype)
            if vtype_id is None:
                tracker.record_rejection(source_file, row_num, f"violation_type_not_found: '{vtype}'", row)
                continue
            count = parse_indian_number(row.get(col), tracker, source_file, row_num, row, col)
            records.append({
                'city_id':           city_id,
                'year':              2023,
                'violation_type_id': vtype_id,
                'source_id':         source_id,
                'accident_count':    count if count is not None else 0,
            })

    out = pd.DataFrame(records)
    if conn is not None:
        conn.execute(text(f'DELETE FROM {SCHEMA}.city_violation_stats'))
        out.to_sql('city_violation_stats', conn, schema=SCHEMA,
                   if_exists='append', index=False, method='multi')
    tracker.increment_loaded(len(out))
    log.info(f"  city_violation_stats: read {len(df_raw)}, loaded {len(out)}")
    return out


def load_city_weather_stats(conn, tracker: ETLTracker) -> pd.DataFrame:
    """Load DataSets/RA2019_A45.csv -> city_weather_stats (unpivoted)."""
    source_file = 'RA2019_A45.csv'
    log.info(f"Loading {source_file} -> city_weather_stats")
    source_id = get_source_id(conn, source_file)
    city_lookup = get_lookup(conn, 'cities', 'city_name', 'city_id')
    weather_lookup = get_lookup(conn, 'weather_conditions', 'weather_condition_name', 'weather_condition_id')

    df_raw = pd.read_csv(DATASETS_DIR / source_file)
    tracker.increment_read(len(df_raw))

    df = df_raw[df_raw['States/UTs'].notna() & (df_raw['States/UTs'].astype(str).str.strip() != 'Total')].copy()
    df['States/UTs'] = df['States/UTs'].apply(normalize_city_name)

    weather_col_map = {
        'Sunny/Clear':     'Sunny/Clear',
        'Rainy':           'Rainy',
        'Foggy and Misty': 'Foggy and Misty',
        'Hail/Sleet':      'Hail/Sleet',
        'Others':          'Others',
    }

    records = []
    for idx, row in df.iterrows():
        row_num = idx + 2
        city_name = row['States/UTs']
        city_id = city_lookup.get(city_name)
        if city_id is None:
            tracker.record_rejection(source_file, row_num, f"city_not_found_in_reference: '{city_name}'", row)
            continue

        for wc_name, prefix in weather_col_map.items():
            wc_id = weather_lookup.get(wc_name)
            if wc_id is None:
                tracker.record_rejection(source_file, row_num, f"weather_condition_not_found: '{wc_name}'", row)
                continue

            acc_col = f'{prefix} - Total Accidents - Number' if prefix == 'Sunny/Clear' else f'{prefix} - Total Accidents'
            kil_col = f'{prefix} - Persons Killed - Number' if prefix == 'Sunny/Clear' else f'{prefix} - Persons Killed'
            grev_col = f'{prefix} - Persons Injured - Greviously Injured'
            minor_col = f'{prefix} - Persons Injured - Minor Injury'
            total_col = f'{prefix} - Persons Injured - Total Injured'

            records.append({
                'city_id':                    city_id,
                'year':                       2019,
                'weather_condition_id':       wc_id,
                'source_id':                  source_id,
                'accident_count':             parse_indian_number(row.get(acc_col, 0), tracker, source_file, row_num, row, acc_col) or 0,
                'persons_killed':             parse_indian_number(row.get(kil_col, 0), tracker, source_file, row_num, row, kil_col) or 0,
                'persons_grievously_injured': parse_indian_number(row.get(grev_col, 0), tracker, source_file, row_num, row, grev_col) or 0,
                'persons_minor_injured':      parse_indian_number(row.get(minor_col, 0), tracker, source_file, row_num, row, minor_col) or 0,
                'persons_total_injured':      parse_indian_number(row.get(total_col, 0), tracker, source_file, row_num, row, total_col) or 0,
            })

    out = pd.DataFrame(records)
    if conn is not None:
        conn.execute(text(f'DELETE FROM {SCHEMA}.city_weather_stats'))
        out.to_sql('city_weather_stats', conn, schema=SCHEMA,
                   if_exists='append', index=False, method='multi')
    tracker.increment_loaded(len(out))
    log.info(f"  city_weather_stats: read {len(df_raw)}, loaded {len(out)}")
    return out


def load_city_road_feature_stats(conn, tracker: ETLTracker) -> pd.DataFrame:
    """Load DataSets/RA2019_A48.csv -> city_road_feature_stats (unpivoted)."""
    source_file = 'RA2019_A48.csv'
    log.info(f"Loading {source_file} -> city_road_feature_stats")
    source_id = get_source_id(conn, source_file)
    city_lookup = get_lookup(conn, 'cities', 'city_name', 'city_id')
    rf_lookup = get_lookup(conn, 'road_features', 'road_feature_name', 'road_feature_id')

    df_raw = pd.read_csv(DATASETS_DIR / source_file)
    tracker.increment_read(len(df_raw))

    df = df_raw.copy()
    df.columns = [re.sub(r'\s+', ' ', c).strip() for c in df.columns]
    df = df[df['State/UT'].notna() & (df['State/UT'].astype(str).str.strip() != 'Total')].copy()
    df['State/UT'] = df['State/UT'].apply(normalize_city_name)

    rf_col_map = {
        'Straight Road':                         'Straight Road',
        'Curved Road':                           'Curved Road',
        'Bridge':                                'Bridge',
        'Culvert':                               'Culvert',
        'Pot Holes':                             'Pot Holes',
        'Steep Grade':                           'Steep Grade',
        'Ongoing Road Works/Under Construction': 'Ongoing Road Works/Under Construction',
        'Others':                                'Others',
    }

    records = []
    for idx, row in df.iterrows():
        row_num = idx + 2
        city_name = row['State/UT']
        city_id = city_lookup.get(city_name)
        if city_id is None:
            tracker.record_rejection(source_file, row_num, f"city_not_found_in_reference: '{city_name}'", row)
            continue

        for rf_name, prefix in rf_col_map.items():
            rf_id = rf_lookup.get(rf_name)
            if rf_id is None:
                tracker.record_rejection(source_file, row_num, f"road_feature_not_found: '{rf_name}'", row)
                continue

            acc_col   = f'{prefix} - Number of Accidents - number' if prefix == 'Straight Road' else f'{prefix} - Number of Accidents'
            kil_col   = f'{prefix} - Persons Killed - Number'       if prefix == 'Straight Road' else f'{prefix} - Persons Killed'
            grev_col  = f'{prefix} - Persons Injured - Greviously Injured'
            minor_col = f'{prefix} - Persons Injured - Minor Injury'
            total_col = f'{prefix} - Persons Injured - Total Injured'

            records.append({
                'city_id':                    city_id,
                'year':                       2019,
                'road_feature_id':            rf_id,
                'source_id':                  source_id,
                'accident_count':             parse_indian_number(row.get(acc_col, 0), tracker, source_file, row_num, row, acc_col) or 0,
                'persons_killed':             parse_indian_number(row.get(kil_col, 0), tracker, source_file, row_num, row, kil_col) or 0,
                'persons_grievously_injured': parse_indian_number(row.get(grev_col, 0), tracker, source_file, row_num, row, grev_col) or 0,
                'persons_minor_injured':      parse_indian_number(row.get(minor_col, 0), tracker, source_file, row_num, row, minor_col) or 0,
                'persons_total_injured':      parse_indian_number(row.get(total_col, 0), tracker, source_file, row_num, row, total_col) or 0,
            })

    out = pd.DataFrame(records)
    if conn is not None:
        conn.execute(text(f'DELETE FROM {SCHEMA}.city_road_feature_stats'))
        out.to_sql('city_road_feature_stats', conn, schema=SCHEMA,
                   if_exists='append', index=False, method='multi')
    tracker.increment_loaded(len(out))
    log.info(f"  city_road_feature_stats: read {len(df_raw)}, loaded {len(out)}")
    return out


def load_collision_type_stats(conn, tracker: ETLTracker) -> pd.DataFrame:
    """Load Data/RoadTypeColl.csv -> collision_type_stats."""
    source_file = 'RoadTypeColl.csv'
    log.info(f"Loading {source_file} -> collision_type_stats")
    source_id = get_source_id(conn, source_file)
    ct_lookup = get_lookup(conn, 'collision_types', 'collision_type_name', 'collision_type_id')

    df_raw = pd.read_csv(DATA_DIR / source_file)
    tracker.increment_read(len(df_raw))

    df = df_raw[
        df_raw['Type of collision'].notna() &
        ~df_raw['Type of collision'].astype(str).str.strip().str.startswith('% ') &
        (df_raw['Type of collision'].astype(str).str.strip() != 'Total')
    ].copy()

    records = []
    for idx, row in df.iterrows():
        row_num = idx + 2
        ct_name = row['Type of collision'].strip()
        ct_id = ct_lookup.get(ct_name)
        if ct_id is None:
            tracker.record_rejection(source_file, row_num, f"collision_type_not_found: '{ct_name}'", row)
            continue

        for yr, acc_col, kil_col, inj_col in [
            (2022, '2022-Accidents', '2022-Killed', '2022-injured'),
            (2023, '2023-Accidents', '2023-Killed', '2023-injured'),
        ]:
            records.append({
                'collision_type_id': ct_id,
                'year':              yr,
                'source_id':         source_id,
                'accident_count':    parse_indian_number(row.get(acc_col), tracker, source_file, row_num, row, acc_col),
                'persons_killed':    parse_indian_number(row.get(kil_col), tracker, source_file, row_num, row, kil_col),
                'persons_injured':   parse_indian_number(row.get(inj_col), tracker, source_file, row_num, row, inj_col),
            })

    out = pd.DataFrame(records)
    if conn is not None:
        conn.execute(text(f'DELETE FROM {SCHEMA}.collision_type_stats'))
        out.to_sql('collision_type_stats', conn, schema=SCHEMA,
                   if_exists='append', index=False, method='multi')
    tracker.increment_loaded(len(out))
    log.info(f"  collision_type_stats: read {len(df_raw)}, loaded {len(out)}")
    return out


def load_violation_type_stats(conn, tracker: ETLTracker) -> pd.DataFrame:
    """Load Data/RoadTypeViol.csv -> violation_type_stats."""
    source_file = 'RoadTypeViol.csv'
    log.info(f"Loading {source_file} -> violation_type_stats")
    source_id = get_source_id(conn, source_file)
    vt_lookup = get_lookup(conn, 'violation_types', 'violation_type_name', 'violation_type_id')

    df_raw = pd.read_csv(DATA_DIR / source_file)
    tracker.increment_read(len(df_raw))

    df = df_raw[
        df_raw['Category'].notna() &
        ~df_raw['Category'].astype(str).str.strip().str.startswith('% ') &
        ~df_raw['Category'].astype(str).str.strip().isin(['All India'])
    ].copy()

    records = []
    for idx, row in df.iterrows():
        row_num = idx + 2
        raw_cat = row['Category'].strip()
        vt_id = vt_lookup.get(raw_cat)
        if vt_id is None:
            tracker.record_rejection(source_file, row_num, f"violation_type_not_found: '{raw_cat}'", row)
            continue

        for yr, acc_col, kil_col, inj_col in [
            (2022, '2022-Accidents', '2022-Killed', '2022-injured'),
            (2023, '2023-Accidents', '2023-Killed', '2023-injured'),
        ]:
            records.append({
                'violation_type_id': vt_id,
                'year':              yr,
                'source_id':         source_id,
                'accident_count':    parse_indian_number(row.get(acc_col), tracker, source_file, row_num, row, acc_col),
                'persons_killed':    parse_indian_number(row.get(kil_col), tracker, source_file, row_num, row, kil_col),
                'persons_injured':   parse_indian_number(row.get(inj_col), tracker, source_file, row_num, row, inj_col),
            })

    out = pd.DataFrame(records)
    if conn is not None:
        conn.execute(text(f'DELETE FROM {SCHEMA}.violation_type_stats'))
        out.to_sql('violation_type_stats', conn, schema=SCHEMA,
                   if_exists='append', index=False, method='multi')
    tracker.increment_loaded(len(out))
    log.info(f"  violation_type_stats: read {len(df_raw)}, loaded {len(out)}")
    return out


# Master list of loaders
LOADERS = [
    ('national_historical_stats', load_ra2019_a1),
    ('national_annual_stats', load_road_no_acc),
    ('state_annual_stats', load_state_stats),
    ('city_accident_stats', load_city_accident_stats),
    ('city_violation_stats', load_city_violation_stats),
    ('city_weather_stats', load_city_weather_stats),
    ('city_road_feature_stats', load_city_road_feature_stats),
    ('collision_type_stats', load_collision_type_stats),
    ('violation_type_stats', load_violation_type_stats),
]


# ================================================================
# ORCHESTRATION & RUN EXECUTION
# ================================================================

def run_etl(conn_str: str | None = None, dry_run: bool = False, verbose: bool = False,
            log_dir: Path | str = 'logs') -> dict:
    """
    Orchestrate ETL execution.
    In live mode:
      - Creates an etl_run_log entry.
      - Executes all loaders inside an atomic engine.begin() transaction.
      - Logs rejected rows and per-table stats.
      - Updates etl_run_log status to COMPLETED or FAILED.
    In dry-run mode:
      - Executes all transformations in-memory.
      - Validates expected counts and returns comprehensive metrics.
    """
    log_dir_path = Path(log_dir)
    log_dir_path.mkdir(parents=True, exist_ok=True)

    git_commit = get_git_commit()
    host_name = get_hostname()

    tracker = ETLTracker()
    start_time = time.time()
    log.info(f"=== ROAD INSIGHT ETL Starting (dry_run={dry_run}, git={git_commit}, host={host_name}) ===")

    engine = None
    run_id = None

    if not dry_run:
        if not conn_str:
            conn_str = os.getenv("DATABASE_URL")
        if not conn_str:
            raise ValueError("Database connection string is required when not in dry-run mode. "
                             "Pass --conn or set DATABASE_URL, or use --dry-run.")
        if create_engine is None:
            raise ImportError("SQLAlchemy is required for live ETL execution.")

        engine = create_engine(conn_str, connect_args={'options': f'-csearch_path={SCHEMA},public'})

        # 1. Initialize master run record (committed independently)
        try:
            with engine.begin() as conn:
                res = conn.execute(text("""
                    INSERT INTO road_insight.etl_run_log (started_at, status, git_commit, host)
                    VALUES (CLOCK_TIMESTAMP(), 'STARTED', :git, :host)
                    RETURNING run_id
                """), {'git': git_commit, 'host': host_name})
                run_id = res.scalar()
                tracker.run_id = run_id
                log.info(f"Initialized ETL run_id = {run_id}")
        except Exception as e:
            log.warning(f"Could not initialize etl_run_log (table might not exist yet): {e}")

    # 2. Execute Loaders
    try:
        if not dry_run and engine is not None:
            # Single transaction atomicity: all loaders run in one begin block
            with engine.begin() as conn:
                for table_name, loader_fn in LOADERS:
                    t0 = time.time()
                    read_before = tracker.rows_read
                    loaded_before = tracker.rows_loaded
                    rej_before = tracker.rows_rejected

                    loader_fn(conn, tracker)

                    t_read = tracker.rows_read - read_before
                    t_loaded = tracker.rows_loaded - loaded_before
                    t_rej = tracker.rows_rejected - rej_before
                    elapsed = time.time() - t0

                    tracker.record_table_log(table_name, t_read, t_loaded, t_rej, elapsed)

                    # Validation check against expected count
                    exp = EXPECTED_COUNTS.get(table_name)
                    if exp is not None and t_loaded != exp:
                        log.warning(f"COUNT WARNING: {table_name} loaded {t_loaded} rows, expected {exp}")

                # Save per-table detail logs
                if tracker.run_id and tracker.table_logs:
                    for t_log in tracker.table_logs:
                        conn.execute(text("""
                            INSERT INTO road_insight.etl_run_table_log
                            (run_id, table_name, rows_read, rows_loaded, rows_rejected, seconds)
                            VALUES (:run_id, :table_name, :rows_read, :rows_loaded, :rows_rejected, :seconds)
                        """), t_log)

                # Save rejected rows
                if tracker.run_id and tracker.rejected_rows:
                    for rej in tracker.rejected_rows:
                        conn.execute(text("""
                            INSERT INTO road_insight.rejected_rows
                            (run_id, source_file, row_number, reason, raw_row)
                            VALUES (:run_id, :source_file, :row_number, :reason, CAST(:raw_row AS jsonb))
                        """), rej)

            # Mark run completed
            if tracker.run_id:
                with engine.begin() as conn:
                    conn.execute(text("""
                        UPDATE road_insight.etl_run_log
                        SET finished_at = CLOCK_TIMESTAMP(),
                            status = 'COMPLETED',
                            rows_read = :read,
                            rows_loaded = :loaded,
                            rows_rejected = :rejected,
                            null_coerced = :nulls
                        WHERE run_id = :run_id
                    """), {
                        'read': tracker.rows_read,
                        'loaded': tracker.rows_loaded,
                        'rejected': tracker.rows_rejected,
                        'nulls': tracker.null_coerced,
                        'run_id': tracker.run_id
                    })
        else:
            # Dry-run execution
            for table_name, loader_fn in LOADERS:
                t0 = time.time()
                read_before = tracker.rows_read
                loaded_before = tracker.rows_loaded
                rej_before = tracker.rows_rejected

                loader_fn(None, tracker)

                t_read = tracker.rows_read - read_before
                t_loaded = tracker.rows_loaded - loaded_before
                t_rej = tracker.rows_rejected - rej_before
                elapsed = time.time() - t0

                tracker.record_table_log(table_name, t_read, t_loaded, t_rej, elapsed)

                exp = EXPECTED_COUNTS.get(table_name)
                if exp is not None and t_loaded != exp:
                    log.warning(f"COUNT WARNING: {table_name} loaded {t_loaded} rows, expected {exp}")
                else:
                    log.info(f"COUNT OK: {table_name} loaded {t_loaded} rows (expected {exp})")

    except Exception as e:
        log.error(f"ETL Execution failed with error: {e}", exc_info=True)
        if not dry_run and engine is not None and tracker.run_id:
            try:
                with engine.begin() as conn:
                    conn.execute(text("""
                        UPDATE road_insight.etl_run_log
                        SET finished_at = CLOCK_TIMESTAMP(),
                            status = 'FAILED'
                        WHERE run_id = :run_id
                    """), {'run_id': tracker.run_id})
            except Exception as update_err:
                log.error(f"Failed to record failure status in etl_run_log: {update_err}")
        raise e

    total_time = time.time() - start_time
    summary = {
        'status': 'SUCCESS',
        'dry_run': dry_run,
        'run_id': tracker.run_id,
        'total_time_seconds': round(total_time, 3),
        'rows_read': tracker.rows_read,
        'rows_loaded': tracker.rows_loaded,
        'rows_rejected': tracker.rows_rejected,
        'null_coerced': tracker.null_coerced,
        'tables': tracker.table_logs,
        'git_commit': git_commit,
        'host': host_name
    }
    log.info(f"=== ROAD INSIGHT ETL Completed in {total_time:.2f}s (Loaded: {tracker.rows_loaded}, Rejected: {tracker.rows_rejected}, NullCoerced: {tracker.null_coerced}) ===")
    return summary


def main():
    parser = argparse.ArgumentParser(description='ROAD INSIGHT Hardened ETL Loader')
    parser.add_argument('--conn', required=False, default=None,
                        help='PostgreSQL connection string (defaults to DATABASE_URL env var)')
    parser.add_argument('--dry-run', action='store_true', default=False,
                        help='Execute parsing and transformations without modifying the database')
    parser.add_argument('--verbose', action='store_true', default=False,
                        help='Enable verbose debug logging')
    parser.add_argument('--log-dir', default='logs',
                        help='Directory to store execution log files')
    args = parser.parse_args()

    # Logging setup
    log_dir = Path(args.log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = log_dir / f"etl_{ts}.log"

    level = logging.DEBUG if args.verbose else logging.INFO
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')

    root_log = logging.getLogger()
    root_log.setLevel(level)

    # Console handler
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(level)
    ch.setFormatter(formatter)
    root_log.addHandler(ch)

    # File handler
    fh = logging.FileHandler(str(log_file), encoding='utf-8')
    fh.setLevel(level)
    fh.setFormatter(formatter)
    root_log.addHandler(fh)

    try:
        summary = run_etl(conn_str=args.conn, dry_run=args.dry_run, verbose=args.verbose, log_dir=log_dir)
        print("\n=== ETL SUMMARY ===")
        print(json.dumps(summary, indent=2))
        sys.exit(0)
    except Exception as e:
        print(f"\nFATAL: ETL run terminated with error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
