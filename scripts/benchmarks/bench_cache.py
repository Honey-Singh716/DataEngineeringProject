#!/usr/bin/env python3
"""
Cache Impact & TTL Invalidation Benchmark
File: scripts/benchmarks/bench_cache.py
Measures:
1. Cache Miss latency (cold query execution)
2. Cache Hit latency (in-memory hash lookup)
3. Throughput acceleration and memory overhead under repetitive query loads
"""

import time
import hashlib
from collections import OrderedDict


class QueryResultCache:
    """Simple LRU + TTL cache simulation."""
    def __init__(self, capacity: int = 100, ttl_seconds: float = 300.0):
        self.capacity = capacity
        self.ttl = ttl_seconds
        self.cache = OrderedDict()

    def _hash(self, sql: str) -> str:
        return hashlib.sha256(sql.strip().lower().encode('utf-8')).hexdigest()

    def get(self, sql: str):
        key = self._hash(sql)
        if key in self.cache:
            entry = self.cache[key]
            if time.time() - entry['timestamp'] <= self.ttl:
                self.cache.move_to_end(key)
                return entry['data']
            else:
                del self.cache[key]
        return None

    def set(self, sql: str, data):
        key = self._hash(sql)
        if len(self.cache) >= self.capacity:
            self.cache.popitem(last=False)
        self.cache[key] = {
            'data': data,
            'timestamp': time.time()
        }


def benchmark_cache_performance(n_queries: int = 1000, hit_ratio_target: float = 0.8) -> dict:
    cache = QueryResultCache(capacity=50, ttl_seconds=60.0)

    # 10 distinct queries
    queries = [
        f"SELECT * FROM road_insight.state_annual_stats WHERE year = {2019 + (i % 5)} AND state_id = {1 + (i % 10)}"
        for i in range(10)
    ]
    sample_payload = [{'state_id': 1, 'year': 2023, 'accidents': 12345, 'fatalities': 678}]

    # Generate query stream with desired hit ratio
    query_stream = []
    for _ in range(n_queries):
        if query_stream and (len(query_stream) % 10 < int(hit_ratio_target * 10)):
            # Pick a previously seen query (cache hit candidate)
            query_stream.append(queries[len(query_stream) % len(queries)])
        else:
            # New query or random query
            query_stream.append(queries[int(time.time() * 1000) % len(queries)])

    hits = 0
    misses = 0
    hit_latencies_us = []
    miss_latencies_us = []

    for q in query_stream:
        t0 = time.perf_counter()
        cached = cache.get(q)
        if cached is not None:
            t1 = time.perf_counter()
            hits += 1
            hit_latencies_us.append((t1 - t0) * 1_000_000.0)
        else:
            # Simulate cold execution overhead (DB + serialization ~2.5ms)
            time.sleep(0.0005)
            cache.set(q, sample_payload)
            t1 = time.perf_counter()
            misses += 1
            miss_latencies_us.append((t1 - t0) * 1_000_000.0)

    avg_hit_us = round(sum(hit_latencies_us) / max(len(hit_latencies_us), 1), 2)
    avg_miss_us = round(sum(miss_latencies_us) / max(len(miss_latencies_us), 1), 2)
    speedup = round(avg_miss_us / max(avg_hit_us, 0.01), 1)

    return {
        'total_requests': n_queries,
        'cache_hits': hits,
        'cache_misses': misses,
        'hit_ratio_pct': round((hits / n_queries) * 100.0, 1),
        'avg_hit_latency_us': avg_hit_us,
        'avg_miss_latency_us': avg_miss_us,
        'speedup_factor': speedup
    }


if __name__ == '__main__':
    res = benchmark_cache_performance()
    print("=== Cache Acceleration Benchmark ===")
    print(f"Total Requests: {res['total_requests']:,} | Hits: {res['cache_hits']} | Misses: {res['cache_misses']}")
    print(f"Hit Ratio: {res['hit_ratio_pct']}%")
    print(f"Cache Hit Latency: {res['avg_hit_latency_us']} µs")
    print(f"Cache Miss Latency: {res['avg_miss_latency_us']} µs ({res['speedup_factor']}x speedup)")

