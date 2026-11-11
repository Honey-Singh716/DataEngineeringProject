#!/usr/bin/env python3
"""
Concurrency & Load Testing Benchmark
File: scripts/benchmarks/bench_load.py
Measures throughput (requests/second) and latency across:
1, 2, 5, 10, and 20 concurrent query worker threads.
"""

import time
import concurrent.futures
from typing import Dict, List


def simulate_query_task(task_id: int, computation_work: int = 5000) -> float:
    t0 = time.perf_counter()
    # CPU-bound hashing + list transformation simulation
    val = task_id
    for _ in range(computation_work):
        val = (val * 1103515245 + 12345) & 0x7FFFFFFF
    t1 = time.perf_counter()
    return (t1 - t0) * 1000.0  # ms


def benchmark_concurrency(worker_counts: List[int] = [1, 2, 5, 10, 20],
                          tasks_per_worker: int = 50) -> Dict[str, dict]:
    results = {}

    for workers in worker_counts:
        total_tasks = workers * tasks_per_worker
        t0 = time.perf_counter()

        latencies = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
            futures = [executor.submit(simulate_query_task, i) for i in range(total_tasks)]
            for fut in concurrent.futures.as_completed(futures):
                latencies.append(fut.result())

        t1 = time.perf_counter()
        total_time = t1 - t0
        rps = round(total_tasks / total_time, 1)
        avg_latency = round(sum(latencies) / len(latencies), 3)

        results[f"workers_{workers}"] = {
            'concurrency': workers,
            'total_tasks': total_tasks,
            'total_seconds': round(total_time, 3),
            'requests_per_sec': rps,
            'avg_latency_ms': avg_latency
        }

    return results


if __name__ == '__main__':
    res = benchmark_concurrency()
    print("=== Concurrency & Load Benchmark ===")
    print(f"{'Concurrency':<12} | {'Tasks':<8} | {'Total Time':<12} | {'RPS (req/s)':<14} | {'Avg Latency (ms)':<16}")
    print("-" * 70)
    for k, v in res.items():
        print(f"{v['concurrency']:<12} | {v['total_tasks']:<8} | {v['total_seconds']:<10} s | {v['requests_per_sec']:<14} | {v['avg_latency_ms']:<16}")

