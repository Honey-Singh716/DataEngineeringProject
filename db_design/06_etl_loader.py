#!/usr/bin/env python3
"""
ROAD INSIGHT — ETL Data Loader
File: 06_etl_loader.py

Transforms raw CSV files → cleaned → PostgreSQL (road_insight schema)

Usage:
    pip install pandas psycopg2-binary sqlalchemy
    python 06_etl_loader.py --conn "postgresql://user:pass@localhost:5432/roadinsight"

The script:
1. Reads raw CSVs
2. Removes aggregate/footnote rows
3. Parses Indian comma-formatted numbers
4. Unpivots wide-format tables to long format
5. Standardizes city/state names
6. Resolves foreign keys using the already-loaded reference data
7. Inserts into normalized core tables
"""

import re
import logging
import argparse
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
log = logging.getLogger(__name__)

# ================================================================
# CONFIGURATION
# ================================================================

DATA_DIR     = r'c:\Users\honey\OneDrive\Desktop\DE(Project)\Data'
DATASETS_DIR = r'c:\Users\honey\OneDrive\Desktop\DE(Project)\DataSets'
SCHEMA       = 'road_insight'

# City name mapping: raw source name → canonical DB name
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

# State name mapping: raw source name → canonical DB name
STATE_NAME_MAP = {
    'j & k #':  'Jammu & Kashmir',
    'j & k':    'Jammu & Kashmir',
    'dadra & nagar haveli*': 'Dadra & Nagar Haveli and Daman & Diu',
}

# ================================================================
# UTILITY FUNCTIONS
# ================================================================

def parse_indian_number(val) -> int | None:
    """Parse Indian comma-formatted numbers like '4,56,959' → 456959."""
    if pd.isna(val):
        return None
    s = str(val).strip()
    if s in ('NA', 'N/A', '#N/A', 'Na', '', '-', '--'):
        return None
    # Remove all commas
    s = s.replace(',', '')
    try:
        return int(float(s))
    except (ValueError, TypeError):
        return None


def parse_float_nullable(val) -> float | None:
    """Parse float; return None for NA-like strings."""
    if pd.isna(val):
        return None
    s = str(val).strip()
    if s in ('NA', 'N/A', '#N/A', 'Na', '', '-', '--'):
        return None
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


def get_lookup(engine, table: str, name_col: str, id_col: str) -> dict:
    """Load a reference table into a name→id dict."""
    with engine.connect() as conn:
        rows = conn.execute(text(
            f'SELECT {name_col}, {id_col} FROM {SCHEMA}.{table}'
        )).fetchall()
    return {row[0]: row[1] for row in rows}


def get_source_id(engine, source_file: str) -> int:
    """Lookup source_id by file name."""
    with engine.connect() as conn:
        row = conn.execute(text(
            f"SELECT source_id FROM {SCHEMA}.data_sources WHERE source_file = :f"
        ), {'f': source_file}).fetchone()
    if row is None:
        raise ValueError(f"source_file '{source_file}' not found in data_sources table. "
                         "Run 05_insert_reference_data.sql first.")
    return row[0]


# ================================================================
# LOADERS
# ================================================================

def load_ra2019_a1(engine):
    """Load DataSets/RA2019_A1.csv → national_historical_stats."""
    log.info("Loading RA2019_A1.csv → national_historical_stats")
    source_id = get_source_id(engine, 'RA2019_A1.csv')

    df = pd.read_csv(f'{DATASETS_DIR}/RA2019_A1.csv')

    # Rename columns (strip trailing whitespace, double spaces)
    df.columns = [re.sub(r'\s+', ' ', c).strip() for c in df.columns]

    # Drop CAGR row and blank rows
    df = df[~df['Years'].astype(str).str.contains('CAGR', na=False)].copy()
    df = df[df['Years'].notna()].copy()

    records = []
    for _, row in df.iterrows():
        year_val = parse_indian_number(row['Years'])
        if year_val is None:
            continue
        records.append({
            'year':                           year_val,
            'source_id':                      source_id,
            'total_accidents':                parse_indian_number(row.get('Total Number of Road Accidents (in numbers)')),
            'total_killed':                   parse_indian_number(row.get('Total Number of Persons Killed (in numbers)')),
            'total_injured':                  parse_indian_number(row.get('Total Number of Persons Injured (in numbers)')),
            'population_thousands':           parse_float_nullable(row.get('Population of India (in thousands)')),
            'registered_vehicles_thousands':  parse_float_nullable(row.get('Total Number of Registered Motor Vehicles (in thousands)')),
            'road_length_km':                 parse_float_nullable(row.get('Road Length (in kms)')),
            'accidents_per_lakh_pop':         parse_float_nullable(row.get('Number of Accidents per Lakh Population')),
            'accidents_per_10k_vehicles':     parse_float_nullable(row.get('Number of Accidents per Ten Thousand Vehicles')),
            'accidents_per_10k_km_roads':     parse_float_nullable(row.get('Number of Accidents per Ten Thousand Kms of Roads')),
            'killed_per_lakh_pop':            parse_float_nullable(row.get('Number of Persons Killed Per Lakh Population')),
            'killed_per_10k_vehicles':        parse_float_nullable(row.get('Number of Persons Killed Per Ten Thousand Vehicles')),
            'killed_per_10k_km_roads':        parse_float_nullable(row.get('Number of Persons Killed per Ten Thousand Kms of Roads')),
            'injured_per_lakh_pop':           parse_float_nullable(row.get('Number of Persons Injured per Lakh Population')),
            'injured_per_10k_vehicles':       parse_float_nullable(row.get('Number of Persons Injured Per Ten Thousand Vehicles')),
            'injured_per_10k_km_roads':       parse_float_nullable(row.get('Number of Persons Injured Per Ten Thousand Kms of Roads')),
        })

    out = pd.DataFrame(records)
    with engine.begin() as conn:
        conn.execute(text(f'DELETE FROM {SCHEMA}.national_historical_stats'))
        out.to_sql('national_historical_stats', conn, schema=SCHEMA,
                   if_exists='append', index=False, method='multi')
    log.info(f"  Inserted {len(out)} rows into national_historical_stats")


def load_road_no_acc(engine):
    """Load Data/RoadNoAcc.csv → national_annual_stats."""
    log.info("Loading RoadNoAcc.csv → national_annual_stats")
    source_id = get_source_id(engine, 'RoadNoAcc.csv')

    df = pd.read_csv(f'{DATA_DIR}/RoadNoAcc.csv')
    # pandas auto-renames duplicate column names with .1, .2
    df.columns = [c.strip() for c in df.columns]
    df = df.dropna(subset=['Year'])

    records = []
    for _, row in df.iterrows():
        year_val = parse_indian_number(row['Year'])
        if year_val is None:
            continue
        # % Change column positions (0=accidents, 1=fatalities, 2=injured)
        pct_cols = [c for c in df.columns if '% Change' in c or 'Pct' in c.lower()]
        records.append({
            'year':                  year_val,
            'source_id':             source_id,
            'total_accidents':       parse_indian_number(row.get('Accidents')),
            'total_fatalities':      parse_indian_number(row.get('Fatalities')),
            'total_injured':         parse_indian_number(row.get('Persons Injured')),
            'accidents_pct_change':  parse_float_nullable(row.iloc[2]) if len(row) > 2 else None,
            'fatalities_pct_change': parse_float_nullable(row.iloc[4]) if len(row) > 4 else None,
            'injured_pct_change':    parse_float_nullable(row.iloc[6]) if len(row) > 6 else None,
        })

    out = pd.DataFrame(records)
    with engine.begin() as conn:
        conn.execute(text(f'DELETE FROM {SCHEMA}.national_annual_stats'))
        out.to_sql('national_annual_stats', conn, schema=SCHEMA,
                   if_exists='append', index=False, method='multi')
    log.info(f"  Inserted {len(out)} rows into national_annual_stats")


def load_state_stats(engine):
    """Load RoadStateWiseAcc.csv + RoadStatewiseKilled.csv → state_annual_stats."""
    log.info("Loading state stats → state_annual_stats")
    source_acc_id = get_source_id(engine, 'RoadStateWiseAcc.csv')
    source_kil_id = get_source_id(engine, 'RoadStatewiseKilled.csv')
    state_lookup = get_lookup(engine, 'states', 'state_name', 'state_id')

    years = [2019, 2020, 2021, 2022, 2023]

    # --- Accidents ---
    df_acc = pd.read_csv(f'{DATA_DIR}/RoadStateWiseAcc.csv')
    # Remove aggregate/footnote rows
    mask_acc = (
        df_acc['State'].notna() &
        ~df_acc['State'].astype(str).str.strip().isin(['All India']) &
        ~df_acc['State'].astype(str).str.startswith('#') &
        ~df_acc['State'].astype(str).str.startswith('*')
    )
    df_acc = df_acc[mask_acc].copy()
    df_acc['State'] = df_acc['State'].apply(normalize_state_name)

    # --- Killed ---
    df_kil = pd.read_csv(f'{DATA_DIR}/RoadStatewiseKilled.csv')
    mask_kil = (
        df_kil['State'].notna() &
        ~df_kil['State'].astype(str).str.strip().isin(['All India']) &
        ~df_kil['State'].astype(str).str.startswith('#') &
        ~df_kil['State'].astype(str).str.startswith('*')
    )
    df_kil = df_kil[mask_kil].copy()
    df_kil['State'] = df_kil['State'].apply(normalize_state_name)

    records = []
    for _, row_acc in df_acc.iterrows():
        state_name = row_acc['State']
        state_id = state_lookup.get(state_name)
        if state_id is None:
            log.warning(f"  State not found in reference: '{state_name}' — skipping")
            continue

        row_kil = df_kil[df_kil['State'] == state_name]

        for yr in years:
            acc_col   = f'{yr} Accidents'
            rank_col  = f'{yr} Ranking'   # from df_acc (accidents CSV)
            kil_col   = f'{yr} Killed'
            krank_col = f'{yr} Ranking'   # from df_kil (killed CSV) — same col name, different df

            acc_count = parse_indian_number(row_acc.get(acc_col))
            acc_rank  = parse_indian_number(row_acc.get(rank_col))
            if acc_rank is not None and (acc_rank < 1 or acc_rank > 50):
                acc_rank = None  # e.g., "#N/A" parsed as garbage number

            killed  = None
            kr      = None
            if len(row_kil) > 0:
                killed = parse_indian_number(row_kil.iloc[0].get(kil_col))
                kr     = parse_indian_number(row_kil.iloc[0].get(krank_col))
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
    with engine.begin() as conn:
        conn.execute(text(f'DELETE FROM {SCHEMA}.state_annual_stats'))
        out.to_sql('state_annual_stats', conn, schema=SCHEMA,
                   if_exists='append', index=False, method='multi')
    log.info(f"  Inserted {len(out)} rows into state_annual_stats")


def load_city_accident_stats(engine):
    """Load Data/LargeCities.csv → city_accident_stats (unpivoted)."""
    log.info("Loading LargeCities.csv → city_accident_stats")
    source_id = get_source_id(engine, 'LargeCities.csv')
    city_lookup = get_lookup(engine, 'cities', 'city_name', 'city_id')

    df = pd.read_csv(f'{DATA_DIR}/LargeCities.csv')
    # Remove total/blank rows
    df = df[df['City'].notna() & (df['City'].astype(str).str.strip() != 'Total')].copy()
    df['City'] = df['City'].apply(normalize_city_name)

    records = []
    for _, row in df.iterrows():
        city_name = row['City']
        city_id = city_lookup.get(city_name)
        if city_id is None:
            log.warning(f"  City not found: '{city_name}' — skipping")
            continue
        for yr in [2022, 2023]:
            records.append({
                'city_id':        city_id,
                'year':           yr,
                'source_id':      source_id,
                'accident_count': parse_indian_number(row.get(f'{yr} Accidents')),
                'persons_killed': parse_indian_number(row.get(f'{yr} Killed')),
                'persons_injured': parse_indian_number(row.get(f'{yr} Injured')),
                'accident_rank':  parse_indian_number(row.get(f'{yr} Ranking Accidents')),
                'killed_rank':    parse_indian_number(row.get(f'{yr} Ranking Killed')),
                'injured_rank':   parse_indian_number(row.get(f'{yr} Ranking Injured')),
            })

    out = pd.DataFrame(records)
    with engine.begin() as conn:
        conn.execute(text(f'DELETE FROM {SCHEMA}.city_accident_stats'))
        out.to_sql('city_accident_stats', conn, schema=SCHEMA,
                   if_exists='append', index=False, method='multi')
    log.info(f"  Inserted {len(out)} rows into city_accident_stats")


def load_city_violation_stats(engine):
    """Load Data/LargeCitiesVio.csv → city_violation_stats (unpivoted)."""
    log.info("Loading LargeCitiesVio.csv → city_violation_stats")
    source_id = get_source_id(engine, 'LargeCitiesVio.csv')
    city_lookup = get_lookup(engine, 'cities', 'city_name', 'city_id')
    vtype_lookup = get_lookup(engine, 'violation_types', 'violation_type_name', 'violation_type_id')

    df = pd.read_csv(f'{DATA_DIR}/LargeCitiesVio.csv')
    df = df[df['City'].notna() & (df['City'].astype(str).str.strip() != 'Total')].copy()
    df['City'] = df['City'].apply(normalize_city_name)

    # Map column names to canonical violation type names
    col_to_vtype = {
        'Overspeeding':             'Over-speeding',
        'Drunken Driving/Drugs use':'Drunken driving/consumption of alcohol & drug',
        'Wrong side driving':       'Driving on wrong side/Lane indiscipline',
        'Jumping red light':        'Jumping red light',
        'Using Mobile Phone':       'Use of mobile phone',
        'Others':                   'Others',
    }

    records = []
    for _, row in df.iterrows():
        city_name = row['City']
        city_id = city_lookup.get(city_name)
        if city_id is None:
            log.warning(f"  City not found: '{city_name}'")
            continue
        for col, vtype in col_to_vtype.items():
            vtype_id = vtype_lookup.get(vtype)
            if vtype_id is None:
                log.error(f"  Violation type not found: '{vtype}'")
                continue
            count = parse_indian_number(row.get(col))
            records.append({
                'city_id':           city_id,
                'year':              2023,   # ASSUMED — verify with source
                'violation_type_id': vtype_id,
                'source_id':         source_id,
                'accident_count':    count if count is not None else 0,
            })

    out = pd.DataFrame(records)
    with engine.begin() as conn:
        conn.execute(text(f'DELETE FROM {SCHEMA}.city_violation_stats'))
        out.to_sql('city_violation_stats', conn, schema=SCHEMA,
                   if_exists='append', index=False, method='multi')
    log.info(f"  Inserted {len(out)} rows into city_violation_stats")


def load_city_weather_stats(engine):
    """Load DataSets/RA2019_A45.csv → city_weather_stats (unpivoted)."""
    log.info("Loading RA2019_A45.csv → city_weather_stats")
    source_id = get_source_id(engine, 'RA2019_A45.csv')
    city_lookup = get_lookup(engine, 'cities', 'city_name', 'city_id')
    weather_lookup = get_lookup(engine, 'weather_conditions', 'weather_condition_name', 'weather_condition_id')

    df = pd.read_csv(f'{DATASETS_DIR}/RA2019_A45.csv')
    df = df[df['States/UTs'].notna() & (df['States/UTs'].astype(str).str.strip() != 'Total')].copy()
    df['States/UTs'] = df['States/UTs'].apply(normalize_city_name)

    # Weather conditions and their column prefixes in source
    weather_col_map = {
        'Sunny/Clear':     'Sunny/Clear',
        'Rainy':           'Rainy',
        'Foggy and Misty': 'Foggy and Misty',
        'Hail/Sleet':      'Hail/Sleet',
        'Others':          'Others',
    }

    records = []
    for _, row in df.iterrows():
        city_name = row['States/UTs']
        city_id = city_lookup.get(city_name)
        if city_id is None:
            log.warning(f"  City not found: '{city_name}'")
            continue
        for wc_name, prefix in weather_col_map.items():
            wc_id = weather_lookup.get(wc_name)
            if wc_id is None:
                log.error(f"  Weather condition not found: '{wc_name}'")
                continue

            # Build column names (with typo correction "Greviously" → "Grievously")
            acc_col = f'{prefix} - Total Accidents - Number' if prefix == 'Sunny/Clear' else f'{prefix} - Total Accidents'
            kil_col = f'{prefix} - Persons Killed - Number' if prefix == 'Sunny/Clear' else f'{prefix} - Persons Killed'
            grev_col = f'{prefix} - Persons Injured - Greviously Injured'   # source typo
            minor_col = f'{prefix} - Persons Injured - Minor Injury'
            total_col = f'{prefix} - Persons Injured - Total Injured '

            records.append({
                'city_id':                    city_id,
                'year':                       2019,
                'weather_condition_id':       wc_id,
                'source_id':                  source_id,
                'accident_count':             parse_indian_number(row.get(acc_col, 0)) or 0,
                'persons_killed':             parse_indian_number(row.get(kil_col, 0)) or 0,
                'persons_grievously_injured': parse_indian_number(row.get(grev_col, 0)) or 0,
                'persons_minor_injured':      parse_indian_number(row.get(minor_col, 0)) or 0,
                'persons_total_injured':      parse_indian_number(row.get(total_col, 0)) or 0,
            })

    out = pd.DataFrame(records)
    with engine.begin() as conn:
        conn.execute(text(f'DELETE FROM {SCHEMA}.city_weather_stats'))
        out.to_sql('city_weather_stats', conn, schema=SCHEMA,
                   if_exists='append', index=False, method='multi')
    log.info(f"  Inserted {len(out)} rows into city_weather_stats")


def load_city_road_feature_stats(engine):
    """Load DataSets/RA2019_A48.csv → city_road_feature_stats (unpivoted)."""
    log.info("Loading RA2019_A48.csv → city_road_feature_stats")
    source_id = get_source_id(engine, 'RA2019_A48.csv')
    city_lookup = get_lookup(engine, 'cities', 'city_name', 'city_id')
    rf_lookup = get_lookup(engine, 'road_features', 'road_feature_name', 'road_feature_id')

    df = pd.read_csv(f'{DATASETS_DIR}/RA2019_A48.csv')
    # Fix double spaces in column names
    df.columns = [re.sub(r'\s+', ' ', c).strip() for c in df.columns]
    df = df[df['State/UT'].notna() & (df['State/UT'].astype(str).str.strip() != 'Total')].copy()
    df['State/UT'] = df['State/UT'].apply(normalize_city_name)

    rf_col_map = {
        'Straight Road':                      'Straight Road',
        'Curved Road':                        'Curved Road',
        'Bridge':                             'Bridge',
        'Culvert':                            'Culvert',
        'Pot Holes':                          'Pot Holes',
        'Steep Grade':                        'Steep Grade',
        'Ongoing Road Works/Under Construction': 'Ongoing Road Works/Under Construction',
        'Others':                             'Others',
    }

    records = []
    for _, row in df.iterrows():
        city_name = row['State/UT']
        city_id = city_lookup.get(city_name)
        if city_id is None:
            log.warning(f"  City not found: '{city_name}'")
            continue
        for rf_name, prefix in rf_col_map.items():
            rf_id = rf_lookup.get(rf_name)
            if rf_id is None:
                log.error(f"  Road feature not found: '{rf_name}'")
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
                'accident_count':             parse_indian_number(row.get(acc_col, 0)) or 0,
                'persons_killed':             parse_indian_number(row.get(kil_col, 0)) or 0,
                'persons_grievously_injured': parse_indian_number(row.get(grev_col, 0)) or 0,
                'persons_minor_injured':      parse_indian_number(row.get(minor_col, 0)) or 0,
                'persons_total_injured':      parse_indian_number(row.get(total_col, 0)) or 0,
            })

    out = pd.DataFrame(records)
    with engine.begin() as conn:
        conn.execute(text(f'DELETE FROM {SCHEMA}.city_road_feature_stats'))
        out.to_sql('city_road_feature_stats', conn, schema=SCHEMA,
                   if_exists='append', index=False, method='multi')
    log.info(f"  Inserted {len(out)} rows into city_road_feature_stats")


def load_collision_type_stats(engine):
    """Load Data/RoadTypeColl.csv → collision_type_stats."""
    log.info("Loading RoadTypeColl.csv → collision_type_stats")
    source_id = get_source_id(engine, 'RoadTypeColl.csv')
    ct_lookup = get_lookup(engine, 'collision_types', 'collision_type_name', 'collision_type_id')

    df = pd.read_csv(f'{DATA_DIR}/RoadTypeColl.csv')
    # Keep only data rows (not % share rows, not Total)
    df = df[
        df['Type of collision'].notna() &
        ~df['Type of collision'].astype(str).str.strip().str.startswith('% ') &
        (df['Type of collision'].astype(str).str.strip() != 'Total')
    ].copy()

    records = []
    for _, row in df.iterrows():
        ct_name = row['Type of collision'].strip()
        ct_id = ct_lookup.get(ct_name)
        if ct_id is None:
            log.warning(f"  Collision type not found: '{ct_name}'")
            continue
        for yr, acc_col, kil_col, inj_col in [
            (2022, '2022-Accidents', '2022-Killed', '2022-injured'),
            (2023, '2023-Accidents', '2023-Killed', '2023-injured'),
        ]:
            records.append({
                'collision_type_id': ct_id,
                'year':              yr,
                'source_id':         source_id,
                'accident_count':    parse_indian_number(row.get(acc_col)),
                'persons_killed':    parse_indian_number(row.get(kil_col)),
                'persons_injured':   parse_indian_number(row.get(inj_col)),
            })

    out = pd.DataFrame(records)
    with engine.begin() as conn:
        conn.execute(text(f'DELETE FROM {SCHEMA}.collision_type_stats'))
        out.to_sql('collision_type_stats', conn, schema=SCHEMA,
                   if_exists='append', index=False, method='multi')
    log.info(f"  Inserted {len(out)} rows into collision_type_stats")


def load_violation_type_stats(engine):
    """Load Data/RoadTypeViol.csv → violation_type_stats."""
    log.info("Loading RoadTypeViol.csv → violation_type_stats")
    source_id = get_source_id(engine, 'RoadTypeViol.csv')
    vt_lookup = get_lookup(engine, 'violation_types', 'violation_type_name', 'violation_type_id')

    df = pd.read_csv(f'{DATA_DIR}/RoadTypeViol.csv')
    df = df[
        df['Category'].notna() &
        ~df['Category'].astype(str).str.strip().str.startswith('% ') &
        ~df['Category'].astype(str).str.strip().isin(['All India'])
    ].copy()

    # Normalize category names to match violation_types reference
    vtype_name_map = {
        'Over-speeding':    'Over-speeding',
        'Drunken driving/consumption of alcohol & drug': 'Drunken driving/consumption of alcohol & drug',
        'Driving on wrong side/Lane indiscipline': 'Driving on wrong side/Lane indiscipline',
        'Jumping red light': 'Jumping red light',
        'Use of mobile phone': 'Use of mobile phone',
        'Others': 'Others',
    }

    records = []
    for _, row in df.iterrows():
        raw_cat = row['Category'].strip()
        vt_name = vtype_name_map.get(raw_cat, raw_cat)
        vt_id = vt_lookup.get(vt_name)
        if vt_id is None:
            log.warning(f"  Violation type not found: '{vt_name}'")
            continue
        for yr, acc_col, kil_col, inj_col in [
            (2022, '2022-Accidents', '2022-Killed', '2022-injured'),
            (2023, '2023-Accidents', '2023-Killed', '2023-injured'),
        ]:
            records.append({
                'violation_type_id': vt_id,
                'year':              yr,
                'source_id':         source_id,
                'accident_count':    parse_indian_number(row.get(acc_col)),
                'persons_killed':    parse_indian_number(row.get(kil_col)),
                'persons_injured':   parse_indian_number(row.get(inj_col)),
            })

    out = pd.DataFrame(records)
    with engine.begin() as conn:
        conn.execute(text(f'DELETE FROM {SCHEMA}.violation_type_stats'))
        out.to_sql('violation_type_stats', conn, schema=SCHEMA,
                   if_exists='append', index=False, method='multi')
    log.info(f"  Inserted {len(out)} rows into violation_type_stats")


# ================================================================
# MAIN
# ================================================================

def main():
    parser = argparse.ArgumentParser(description='ROAD INSIGHT ETL Loader')
    parser.add_argument('--conn', required=True,
                        help='PostgreSQL connection string: postgresql://user:pass@host:port/db')
    args = parser.parse_args()

    engine = create_engine(args.conn, connect_args={'options': f'-csearch_path={SCHEMA},public'})

    log.info("=== ROAD INSIGHT ETL Starting ===")
    load_ra2019_a1(engine)
    load_road_no_acc(engine)
    load_state_stats(engine)
    load_city_accident_stats(engine)
    load_city_violation_stats(engine)
    load_city_weather_stats(engine)
    load_city_road_feature_stats(engine)
    load_collision_type_stats(engine)
    load_violation_type_stats(engine)
    log.info("=== ROAD INSIGHT ETL Complete ===")


if __name__ == '__main__':
    main()
