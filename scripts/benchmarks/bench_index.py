#!/usr/bin/env python3
"""
Index Performance & Scan Access Path Benchmark
File: scripts/benchmarks/bench_index.py
Compares:
1. Full Sequential Scan (unindexed O(N) scan)
2. B-Tree / Index Scan (O(log N) lookup)
3. Bitmap Index Scan (range & multi-match scan)
"""

import time
import bisect
import random
from pathlib import Path
import numpy as np
import pandas as pd


def benchmark_index_scans(n_records: int = 200000, n_queries: int = 500) -> dict:
    # 1. Generate realistic dataset mimicking accident data
    random.seed(42)
    np.random.seed(42)

    years = np.random.choice([2019, 2020, 2021, 2022, 2023], size=n_records)
    state_ids = np.random.randint(1, 38, size=n_records)
    city_ids = np.random.randint(1, 51, size=n_records)
    accidents = np.random.randint(10, 50000, size=n_records)

    df = pd.DataFrame({
        'year': years,
        'state_id': state_ids,
        'city_id': city_ids,
        'accident_count': accidents
    })

    # Prepare index structures
    # B-Tree index simulation: sorted key list with binary search
    sorted_df = df.sort_values(by=['state_id', 'year']).reset_index(drop=True)
    sorted_keys = list(zip(sorted_df['state_id'], sorted_df['year']))

    # Hash / Inverted Bitmap index simulation
    state_bitmap = {}
    for idx, sid in enumerate(df['state_id']):
        if sid not in state_bitmap:
            state_bitmap[sid] = []
        state_bitmap[sid].append(idx)

    # Sample query targets
    test_queries = [(random.randint(1, 37), random.choice([2019, 2020, 2021, 2022, 2023])) for _ in range(n_queries)]

    # 1. Full Sequential Scan (unindexed)
    t0 = time.perf_counter()
    matches_seq = 0
    raw_tuples = list(zip(df['state_id'], df['year'], df['accident_count']))
    for sid, yr in test_queries:
        res = [row for row in raw_tuples if row[0] == sid and row[1] == yr]
        matches_seq += len(res)
    t1 = time.perf_counter()
    dur_seq = (t1 - t0) * 1000.0  # ms

    # 2. B-Tree / Index Scan (binary search over sorted composite key)
    t0 = time.perf_counter()
    matches_btree = 0
    for target in test_queries:
        idx_left = bisect.bisect_left(sorted_keys, target)
        idx_right = bisect.bisect_right(sorted_keys, target)
        matches_btree += (idx_right - idx_left)
    t1 = time.perf_counter()
    dur_btree = (t1 - t0) * 1000.0  # ms

    # 3. Bitmap Index Scan (posting list union/intersection)
    t0 = time.perf_counter()
    matches_bitmap = 0
    for sid, yr in test_queries:
        row_ids = state_bitmap.get(sid, [])
        # filter matching bitmap rows by year
        hits = [rid for rid in row_ids if df['year'].iloc[rid] == yr]
        matches_bitmap += len(hits)
    t1 = time.perf_counter()
    dur_bitmap = (t1 - t0) * 1000.0  # ms

    speedup_btree = round(dur_seq / max(dur_btree, 0.0001), 1)
    speedup_bitmap = round(dur_seq / max(dur_bitmap, 0.0001), 1)

    return {
        'n_records': n_records,
        'n_queries': n_queries,
        'seq_scan_ms': round(dur_seq, 2),
        'seq_avg_us': round((dur_seq / n_queries) * 1000, 2),
        'btree_scan_ms': round(dur_btree, 2),
        'btree_avg_us': round((dur_btree / n_queries) * 1000, 2),
        'bitmap_scan_ms': round(dur_bitmap, 2),
        'bitmap_avg_us': round((dur_bitmap / n_queries) * 1000, 2),
        'speedup_btree': speedup_btree,
        'speedup_bitmap': speedup_bitmap
    }


if __name__ == '__main__':
    r = benchmark_index_scans()
    print("=== Index Scan Access Path Benchmark ===")
    print(f"Dataset Size: {r['n_records']:,} rows | Queries Tested: {r['n_queries']}")
    print(f"Sequential Scan: {r['seq_scan_ms']} ms ({r['seq_avg_us']} µs/query)")
    print(f"B-Tree Index Scan: {r['btree_scan_ms']} ms ({r['btree_avg_us']} µs/query) — {r['speedup_btree']}x faster")
    print(f"Bitmap Index Scan: {r['bitmap_scan_ms']} ms ({r['bitmap_avg_us']} µs/query) — {r['speedup_bitmap']}x faster")
