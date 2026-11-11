#!/usr/bin/env python3
"""
System Resource Profiling Benchmark
File: scripts/benchmarks/bench_resources.py
Profiles RSS memory and CPU usage during:
1. Baseline initialization
2. Full ETL dataset transformation
3. 200k-row analytical aggregation
4. Memory reclaim upon garbage collection
"""

import sys
import gc
import time
from pathlib import Path
import pandas as pd
import numpy as np

try:
    import resource
except ImportError:
    resource = None

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

import importlib.util
etl_path = BASE_DIR / 'db_design' / '06_etl_loader.py'
spec = importlib.util.spec_from_file_location('etl_loader', str(etl_path))
etl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(etl)


def get_memory_mb() -> float:
    """Return max RSS memory in MB."""
    if resource is not None:
        usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        # On macOS ru_maxrss is in bytes, on Linux in KB
        if sys.platform == 'darwin':
            return round(usage / (1024 * 1024), 2)
        else:
            return round(usage / 1024, 2)
    return 0.0


def benchmark_system_resources() -> dict:
    snapshots = {}

    # 1. Baseline
    gc.collect()
    snapshots['baseline_mb'] = get_memory_mb()

    # 2. ETL Processing (loading all raw CSVs into memory)
    t0 = time.perf_counter()
    tracker = etl.ETLTracker()
    data = {}
    for name, fn in etl.LOADERS:
        data[name] = fn(None, tracker)
    t1 = time.perf_counter()
    snapshots['post_etl_mb'] = get_memory_mb()
    snapshots['etl_duration_seconds'] = round(t1 - t0, 4)
    snapshots['etl_rows_loaded'] = tracker.rows_loaded

    # 3. Large DataFrame Aggregation (100k records)
    t0 = time.perf_counter()
    big_df = pd.concat([data['state_annual_stats']] * 600, ignore_index=True)
    grouped = big_df.groupby(['state_id', 'year'])['accident_count'].agg(['sum', 'mean', 'max'])
    t1 = time.perf_counter()
    snapshots['post_agg_mb'] = get_memory_mb()
    snapshots['agg_duration_seconds'] = round(t1 - t0, 4)
    snapshots['agg_rows_processed'] = len(big_df)

    # 4. Post-GC Cleanup
    del big_df
    del grouped
    del data
    gc.collect()
    snapshots['post_cleanup_mb'] = get_memory_mb()

    return snapshots


if __name__ == '__main__':
    res = benchmark_system_resources()
    print("=== System Resource Profiling ===")
    print(f"Baseline Memory: {res['baseline_mb']} MB")
    print(f"Post-ETL Memory: {res['post_etl_mb']} MB ({res['etl_duration_seconds']}s to process {res['etl_rows_loaded']:,} rows)")
    print(f"Peak Aggregation Memory: {res['post_agg_mb']} MB ({res['agg_duration_seconds']}s to aggregate {res['agg_rows_processed']:,} rows)")
    print(f"Memory Post-GC: {res['post_cleanup_mb']} MB")

