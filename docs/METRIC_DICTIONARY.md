# RoadInsight India — Metric Dictionary & Statistical Formulations

## Purpose
This document provides mathematical formulations, semantic definitions, underlying denominators, edge cases, and source lineage for all road safety and accident metrics used across the RoadInsight India data warehouse and analytics dashboards.

---

## 1. Metric Specification Matrix

| Metric Code | Metric Name | Mathematical Formula | Denominator Definition | Unit | Fact Table & Column | Null / Edge Case Handling |
|---|---|---|---|---|---|---|
| `MET-01` | **Total Accidents** | $\sum \text{accidents}$ | N/A (Atomic count) | Integer count | `national_annual_stats.total_accidents`, `state_annual_stats.accident_count` | 0 = certified zero; NULL = missing/unreported |
| `MET-02` | **Total Fatalities (Killed)** | $\sum \text{persons\_killed}$ | N/A (Atomic count) | Integer count | `national_annual_stats.total_fatalities`, `state_annual_stats.persons_killed` | 0 = certified zero; NULL = missing/unreported |
| `MET-03` | **Total Injured** | $\sum \text{persons\_injured}$ | N/A (Atomic count) | Integer count | `national_annual_stats.total_injured`, `city_accident_stats.persons_injured` | In city weather stats, known non-additivity with grievous/minor is documented |
| `MET-04` | **Accident Severity / Fatality Rate** | $\frac{\text{Total Killed}}{\text{Total Accidents}} \times 100$ | Total Accidents | Fatalities per 100 accidents (%) | Computed view: `v_state_summary.accident_severity` | If `accidents == 0` or NULL, return NULL to prevent division by zero |
| `MET-05` | **Accidents per Lakh Population** | $\frac{\text{Total Accidents}}{\text{Population in Thousands} \times 10} \times 10^5 = \frac{\text{Total Accidents}}{\text{Population in Thousands}} \times 100$ | Mid-year estimated population in thousands (Census of India) | Accidents per 100,000 persons | `national_historical_stats.accidents_per_lakh_pop` | Populated for national historical stats (1970–2019) |
| `MET-06` | **Fatalities per Lakh Population** | $\frac{\text{Total Killed}}{\text{Population in Thousands}} \times 100$ | Mid-year estimated population in thousands | Fatalities per 100,000 persons | `national_historical_stats.killed_per_lakh_pop` | If population is NULL, rate is NULL |
| `MET-07` | **Accidents per 10,000 Vehicles** | $\frac{\text{Total Accidents}}{\text{Registered Vehicles in Thousands}} \times 10$ | Total registered motor vehicles in thousands (MoRTH Transport Research Wing) | Accidents per 10,000 motor vehicles | `national_historical_stats.accidents_per_10k_vehicles` | Denominator excludes non-motorized vehicles |
| `MET-08` | **Fatalities per 10,000 Vehicles** | $\frac{\text{Total Killed}}{\text{Registered Vehicles in Thousands}} \times 10$ | Total registered motor vehicles in thousands | Fatalities per 10,000 motor vehicles | `national_historical_stats.killed_per_10k_vehicles` | Normalizes state/national risk against motorization growth |
| `MET-09` | **Accidents per 10,000 km Roads** | $\frac{\text{Total Accidents}}{\text{Road Length in km}} \times 10000$ | Total surfaced and unsurfaced road length in kilometers | Accidents per 10,000 km road network | `national_historical_stats.accidents_per_10k_km_roads` | Excludes pedestrian pathways and unclassified rural tracks |
| `MET-10` | **Fatalities per 10,000 km Roads** | $\frac{\text{Total Killed}}{\text{Road Length in km}} \times 10000$ | Total road length in kilometers | Fatalities per 10,000 km road network | `national_historical_stats.killed_per_10k_km_roads` | Infrastructure safety density proxy |
| `MET-11` | **Year-over-Year Accident % Change** | $\frac{\text{Accidents}_t - \text{Accidents}_{t-1}}{\text{Accidents}_{t-1}} \times 100$ | Prior year accident count ($\text{Accidents}_{t-1}$) | Percentage (%) | `national_annual_stats.accidents_pct_change` | 2020 experienced -18.6% drop due to nationwide COVID lockdown |
| `MET-12` | **Year-over-Year Fatality % Change** | $\frac{\text{Fatalities}_t - \text{Fatalities}_{t-1}}{\text{Fatalities}_{t-1}} \times 100$ | Prior year fatality count ($\text{Fatalities}_{t-1}$) | Percentage (%) | `national_annual_stats.fatalities_pct_change` | 2020 experienced -13.0% drop |
| `MET-13` | **Year-over-Year Injured % Change** | $\frac{\text{Injured}_t - \text{Injured}_{t-1}}{\text{Injured}_{t-1}} \times 100$ | Prior year injured count ($\text{Injured}_{t-1}$) | Percentage (%) | `national_annual_stats.injured_pct_change` | 2020 experienced -22.8% drop |
| `MET-14` | **State Accident Rank** | $\text{DENSE\_RANK}() \text{ OVER } (\text{ORDER BY accidents DESC})$ | National ranking across 37 states & UTs | Rank integer (1 to 50) | `state_annual_stats.accident_rank` | Values outside 1..50 rejected by CHECK constraint |
| `MET-15` | **State Fatality Rank** | $\text{DENSE\_RANK}() \text{ OVER } (\text{ORDER BY killed DESC})$ | National ranking across 37 states & UTs | Rank integer (1 to 50) | `state_annual_stats.killed_rank` | Values outside 1..50 rejected by CHECK constraint |
| `MET-16` | **City Accident Rank** | Rank within 50 million-plus cities | 50 million-plus cities covered by MoRTH | Rank integer (1 to 50) | `city_accident_stats.accident_rank` | Ranked by accident volume |
| `MET-17` | **City Fatality Rank** | Rank within 50 million-plus cities | 50 million-plus cities covered by MoRTH | Rank integer (1 to 50) | `city_accident_stats.killed_rank` | Ranked by fatality volume |

---

## 2. Statistical Nuances & Denominator Boundaries

### 2.1 Census Projections vs Actual Census
- Population figures between 2011 and 2019 are based on official Registrar General of India (RGI) mid-year population projections.
- In 2020 and onward, decennial census data collection was postponed; hence, rates relying on population are not extrapolated post-2019 without explicit projection metadata.

### 2.2 Vehicle Registration Inflation
- `registered_vehicles_thousands` includes all cumulatively registered vehicles in state transport databases (Vahan portal). Because vehicle scrappage was historically under-recorded in India prior to the National Vehicle Scrappage Policy, the registered fleet denominator includes inactive/scrapped vehicles, meaning true per-vehicle accident rates on active vehicles are slightly higher than published figures.

