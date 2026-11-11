# RoadInsight India — Master Evidence & Audit Report

**Report Generation Timestamp:** 2026-11-11 17:43:26 UTC  
**Repository Branch:** `feature/hardening`  
**Purpose:** Consolidated, traceable record of all empirical benchmarks, data quality verifications, index analyses, and test executions. Every metric in this report links directly to a versioned evidence file.

---

## 1. Traceability Index & Evidence Directory

| Domain | Primary Evidence Source | Key Metrics Recorded |
|---|---|---|
| **Baseline & Bug Repro** | [`docs/evidence/00_baseline/baseline_summary.md`](evidence/00_baseline/baseline_summary.md) | Initial code metrics, dependencies, reproduction of B1-B8 defects |
| **Data Quality & Reconciliation** | [`docs/evidence/dq/dq_report_latest.md`](evidence/dq/dq_report_latest.md) | 14 checks (R1-R6, Q1-Q8), 100% mathematical reconciliation, Annexure 45 upstream limitation |
| **Index Redundancy Catalog** | [`docs/evidence/indexes/redundant_index_analysis.md`](evidence/indexes/redundant_index_analysis.md) | 12 redundant indexes identified & dropped (~41.4% reduction in manual indexes) |
| **Golden Queries Benchmark** | [`docs/evidence/golden/golden_results.csv`](evidence/golden/golden_results.csv) | 30 benchmark queries: 20 supported SQL, 5 unsupported, 5 adversarial security attacks |
| **Bottleneck & System Benchmarks** | [`docs/evidence/benchmarks/BOTTLENECK_SUMMARY.md`](evidence/benchmarks/BOTTLENECK_SUMMARY.md) | Ingestion throughput, B-Tree vs Seq scan speedup, pipeline stage latencies, memory profile |
| **Test Matrix & Coverage** | [`docs/evidence/tests/test_summary.md`](evidence/tests/test_summary.md) | Automated pytest suites, secret scanning, ETL edge cases, manual test log |

---

## 2. Core Quantitative Findings (Evidence-Linked)

### 2.1 Data Quality & Mathematical Reconciliation
*Source: [`docs/evidence/dq/dq_report_latest.json`](evidence/dq/dq_report_latest.json)*
- **Total Automated Checks**: 14
- **Passed**: **13** | **Documented Warnings**: **1** | **Failures**: **0**
- **State-to-National Reconciliation (R1)**:
  - 2019: National = 456,959 | State Sum = 456,959 (0.00% difference)
  - 2020: National = 372,181 | State Sum = 372,181 (0.00% difference)
  - 2021: National = 412,432 | State Sum = 412,432 (0.00% difference)
  - 2022: National = 461,312 | State Sum = 461,312 (0.00% difference)
  - 2023: National = 480,583 | State Sum = 480,583 (0.00% difference)
- **Documented Upstream Source Anomaly (Q6)**:
  - In `RA2019_A45.csv` (MoRTH Annexure 45), 161 of 250 records exhibit non-additive injury totals (`Total Injured != Grievously Injured + Minor Injured`). Preserved verbatim in compliance with raw government data audit guidelines.

### 2.2 Golden Queries Evaluation
*Source: [`docs/evidence/golden/golden_results.csv`](evidence/golden/golden_results.csv)*
- **Evaluated Queries**: 30 queries
- **Supported Domain Questions (GQ-01 to GQ-20)**: 20/20 valid SELECT SQL generated with 100% AST schema conformance.
- **Unsupported Out-of-Scope Questions (GQ-21 to GQ-25)**: 5/5 correctly identified and rejected without AI hallucinations.
- **Adversarial Security Injection Attacks (GQ-26 to GQ-30)**: 5/5 blocked by multi-layer AST and keyword guardrails.

### 2.3 System Performance & Empirical Benchmarks
*Source: [`docs/evidence/benchmarks/BOTTLENECK_SUMMARY.md`](evidence/benchmarks/BOTTLENECK_SUMMARY.md)*
- **Sequential Scan vs B-Tree Index Scan**:
  - Full sequential scan over 200,000 rows required ~1,679 ms.
  - B-tree composite index scan required ~1.32 ms (**>1,200x speedup**).
- **Ingestion Throughput**:
  - Streaming buffer COPY and Pandas multi-row values achieve over 150,000 rows/second, outperforming individual row iteration.
- **Interactive Latency Profile**:
  - In-database query execution takes < 5 ms; LLM API generation represents ~90% of total interactive latency.

### 2.4 Index Optimization
*Source: [`docs/evidence/indexes/redundant_index_analysis.md`](evidence/indexes/redundant_index_analysis.md)*
- **12 Redundant Indexes Dropped**:
  - 5 exact duplicate indexes backed by UNIQUE constraints (`idx_nat_hist_year`, `idx_nat_ann_year`, `idx_state_stats_state_year`, `idx_city_acc_city_year`, `idx_city_vio_city_year_type`).
  - 7 leading-prefix redundant indexes covered by composite B-trees (`idx_state_stats_state_id`, `idx_city_acc_city_id`, `idx_city_vio_city_id`, `idx_city_wea_city_id`, `idx_city_rf_city_id`, `idx_coll_type_id`, `idx_viol_type_id`).
  - Result: 41.4% reduction in manual index definitions, eliminating write amplification without query regression.

---

## 3. Feedback Alignment Verification
*Source: [`docs/FEEDBACK_TRACEABILITY.md`](FEEDBACK_TRACEABILITY.md)*
Every criticism raised in university evaluation has been directly addressed with executable code and reproducible evidence:
1. *Vague statements replaced with verifiable metrics*: 100% of reported numbers originate from executed scripts.
2. *Documented denominators*: All statistical formulas and edge cases codified in [`docs/METRIC_DICTIONARY.md`](METRIC_DICTIONARY.md).
3. *Tested edge cases*: Non-integer string rejection, Daman & Diu 0 vs NULL semantics, and multi-statement injection blocking automated in test suites.
4. *No silent failures*: Rejected rows persisted into `road_insight.rejected_rows` with complete diagnostic JSON.
