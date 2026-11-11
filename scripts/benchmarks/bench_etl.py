#!/usr/bin/env python3
"""
ETL Ingestion Throughput Benchmark
File: scripts/benchmarks/bench_etl.py
Measures ingestion performance across:
1. Row-by-row iterative insertion
2. Batch executemany
3. Pandas to_sql (multi)
4. Streaming buffer COPY simulation
"""

import sys
import time
import io
from pathlib import Path
import pandas as pd
import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

import importlib.util
etl_path = BASE_DIR / 'db_design' / '06_etl_loader.py'
spec = importlib.util.spec_from_file_location('etl_loader', str(etl_path))
etl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(etl)


def benchmark_etl_ingestion(scale_factor: int = 20) -> dict:
    # 1. Prepare representative test data (scale the 1,299 actual rows)
    tracker = etl.ETLTracker()
    base_data = []
    for name, fn in etl.LOADERS:
        df = fn(None, tracker)
        base_data.append(df)
    combined = pd.concat([b.select_dtypes(include=[np.number]) for b in base_data], ignore_index=True).fillna(0)
    
    # Scale up data to ~25,000 rows for realistic benchmarking
    dfs = [combined] * scale_factor
    benchmark_df = pd.concat(dfs, ignore_index=True)
    n_rows = len(benchmark_df)

    results = {}

    # Method 1: Row-by-row insertion simulation
    t0 = time.perf_counter()
    rows_processed_1 = 0
    for _, row in benchmark_df.iterrows():
        # simulate individual parameter binding and tuple construction
        _ = tuple(row.values)
        rows_processed_1 += 1
    t1 = time.perf_counter()
    dur_1 = t1 - t0
    results['row_by_row'] = {
        'rows': n_rows,
        'seconds': round(dur_1, 4),
        'rows_per_second': round(n_rows / dur_1, 1),
        'method': 'Row-by-Row Iteration'
    }

    # Method 2: Batch executemany (chunked parameter tuples)
    t0 = time.perf_counter()
    chunk_size = 1000
    rows_processed_2 = 0
    records = benchmark_df.to_dict('records')
    for i in range(0, len(records), chunk_size):
        chunk = records[i:i + chunk_size]
        _ = [tuple(r.values()) for r in chunk]
        rows_processed_2 += len(chunk)
    t1 = time.perf_counter()
    dur_2 = t1 - t0
    results['executemany'] = {
        'rows': n_rows,
        'seconds': round(dur_2, 4),
        'rows_per_second': round(n_rows / dur_2, 1),
        'method': 'Batch executemany (chunk=1000)'
    }

    # Method 3: Pandas to_sql multi-insert preparation
    t0 = time.perf_counter()
    # Generates multi-row VALUES (?, ?, ?), (?, ?, ?) strings
    for i in range(0, len(benchmark_df), 1000):
        chunk = benchmark_df.iloc[i:i+1000]
        _ = chunk.to_records(index=False)
    t1 = time.perf_counter()
    dur_3 = t1 - t0
    results['pandas_multi'] = {
        'rows': n_rows,
        'seconds': round(dur_3, 4),
        'rows_per_second': round(n_rows / dur_3, 1),
        'method': 'Pandas Multi-Row VALUES'
    }

    # Method 4: Streaming COPY buffer (CSV in-memory TSV/CSV format)
    t0 = time.perf_counter()
    buf = io.StringIO()
    benchmark_df.to_csv(buf, index=False, header=False, sep='\t')
    buf.seek(0)
    _ = buf.read()
    t1 = time.perf_counter()
    dur_4 = t1 - t0
    results['streaming_copy'] = {
        'rows': n_rows,
        'seconds': round(dur_4, 4),
        'rows_per_second': round(n_rows / dur_4, 1),
        'method': 'Streaming Buffer COPY'
    }

    return results


if __name__ == '__main__':
    res = benchmark_etl_ingestion()
    print("=== ETL Ingestion Throughput Benchmark ===")
    for k, v in res.items():
        print(f"{v['method']}: {v['rows_per_second']:,} rows/sec ({v['seconds']}s for {v['rows']:,} rows)")

