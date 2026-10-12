# BUSINESS GLOSSARY — ROAD INSIGHT
## AI-Powered Indian Road Accident Analysis System
**Version:** 1.0 | **Date:** 2026-09-21

Only terms directly supported by actual source datasets are defined below.
Ambiguities are explicitly documented.

---

## CORE TERMS

### Accident / Road Accident
A road traffic accident resulting in injury or death to persons.
In this database, accident counts refer to the number of reported road accidents
as recorded by police and compiled by MoRTH (Ministry of Road Transport and Highways).

**AMBIGUITY:** The source data does not define the threshold for what constitutes
a recordable accident (e.g., minimum injury severity, property-damage-only incidents).
This follows the official MoRTH reporting definition.

**Synonyms:** Crash, Incident, Road crash, Traffic accident, Collision (context-dependent)

---

### Fatality / Person Killed
A person who dies as a result of a road accident.
Source data uses "Killed" and "Fatalities" interchangeably.

**IMPORTANT NOTE:**
- "Killed" in RoadStatewiseKilled.csv = persons killed
- "Fatalities" in RoadNoAcc.csv = same concept
- Both map to `persons_killed` in the normalized schema.

**Synonyms:** Death, Fatality, Road death, Killed

---

### Person Injured
A person who sustains non-fatal injuries in a road accident.

**SUBCATEGORIES (from RA2019_A45.csv, RA2019_A48.csv only):**
- **Grievously Injured:** Seriously/severely injured (source spelling: "Greviously" — corrected)
- **Minor Injured:** Minor injuries
- **Total Injured:** Sum of grievously + minor injured

**AMBIGUITY:** Source data does not define the clinical threshold between
grievously injured and minor injured. This follows MoRTH classification.

**Synonyms:** Injured, Hurt, Wounded

---

### Accident Count
Total number of reported road accidents in a geographic area for a given year.

---

### Fatality Rate
The number of fatalities per unit of accidents or population.
Computed as:
- Fatalities / (Population / 100,000) = Fatalities per lakh population
- Fatalities / Accidents = Case fatality rate (not directly stored; computable)

**STORED IN:** national_historical_stats (per lakh population, per 10K vehicles, per 10K km roads)

---

### State / UT
An Indian State or Union Territory as classified under the Constitution of India.
37 States/UTs appear in source data.

**NOTE:** Due to administrative reorganizations:
- Ladakh became a separate UT in October 2019; data before 2021 is under Jammu & Kashmir.
- Daman & Diu was merged with Dadra & Nagar Haveli from January 2020.

---

### Union Territory (UT)
A type of Indian administrative unit directly governed by the Central Government.
Distinct from States, which have their own legislative assemblies.

---

### Large City
One of the 50 large Indian cities tracked in MoRTH city-level road accident reports.
Selection criteria for "large city" is defined by MoRTH (typically population above a threshold).
The exact selection criteria are NOT documented in the source datasets.

---

### Collision Type
The manner in which a road accident occurred.
Defined by MoRTH and used in RoadTypeColl.csv.

**Values:**
| Term | Definition |
|------|-----------|
| Hit and Run | Offending vehicle fled the scene after the accident |
| With parked Vehicle | Collision with a vehicle parked on the road |
| Hit from Back | Rear-end collision |
| Hit from side | Side-impact collision |
| Run off Road | Vehicle left the road surface |
| Fixed object | Collision with a stationary roadside structure or object |
| Vehicle overturn | Vehicle rolled or overturned |
| Head on collision | Front-to-front collision between opposing vehicles |
| Others | Not classified in the above categories |

---

### Violation Type / Traffic Violation Cause
The traffic law violation or driver behavior identified as the primary cause of an accident.
Defined by MoRTH.

**Values:**
| Term | Definition |
|------|-----------|
| Over-speeding | Driving at or above the speed limit more than permitted |
| Drunken driving / alcohol & drug | Driving under influence of alcohol or drugs |
| Driving on wrong side / Lane indiscipline | Wrong-way driving or improper lane use |
| Jumping red light | Running a red traffic signal |
| Use of mobile phone | Using a mobile phone while driving |
| Others | Causes not classified above |

**NOTE:** A single accident may have multiple causes but is recorded under one primary cause.

---

### Weather Condition
The weather at the time and location of the accident.
Classified by MoRTH in 2019 city-level data.

**Values:** Sunny/Clear, Rainy, Foggy and Misty, Hail/Sleet, Others

---

### Road Feature
The type of road infrastructure at or near the accident location.
Classified by MoRTH in 2019 city-level data.

**Values:** Straight Road, Curved Road, Bridge, Culvert, Pot Holes, Steep Grade,
Ongoing Road Works/Under Construction, Others

---

### Accident Rank / Ranking
The ordinal rank of a state or city among all states/cities ordered by accident count
(or killed count, or injured count) in a given year.
Rank 1 = highest accident count.

**IMPORTANT:** Rankings are among the set present in source data (37 states/UTs or 50 cities).

---

### Lakh
An Indian numbering unit = 100,000 (one hundred thousand).
Used in rate calculations (e.g., accidents per lakh population).

---

### Road Length
Total length of roads in India (in kilometers).
Used as a denominator for road density-based accident rates.
**Available for years:** 1970–2018 (NULL for 2019 in source data).

---

### Registered Motor Vehicles
Total number of vehicles registered with transport authorities (in thousands).
Used as a denominator for vehicle density-based accident rates.

---

### CAGR (Compound Annual Growth Rate)
A measure of the mean annual growth rate over a specified time period.
Appears in RA2019_A1.csv as "CAGR 2009/2019".
**This row is EXCLUDED from database loading** — it is a computed summary, not a year observation.

---

## METRIC SYNONYMS FOR TEXT-TO-SQL

| Business Term | Database Column |
|--------------|----------------|
| Deaths | persons_killed |
| Fatalities | persons_killed |
| Casualties | persons_killed (context-dependent — may include injured) |
| Accidents | accident_count |
| Crashes | accident_count |
| Injuries | persons_injured |
| Hurt | persons_injured |
| Wounded | persons_injured |
| Year | year |
| Annual | year |
| State | states.state_name |
| Region | states.state_name (no region entity in database) |
| City | cities.city_name |
| Urban area | cities.city_name |
| Collision type | collision_types.collision_type_name |
| Cause | violation_types.violation_type_name |
| Weather | weather_conditions.weather_condition_name |
| Road type | road_features.road_feature_name |

---

## AMBIGUITIES NOT RESOLVED

| Term | Ambiguity |
|------|-----------|
| "Vizaq" | Source short form; assumed Visakhapatnam — not confirmed |
| "Others" (all lookup tables) | Definition unknown — catch-all category |
| Year for LargeCitiesVio.csv | Assumed 2023; not explicitly stated in source |
| "Casualties" | Could mean killed only, or killed + injured — avoid without context |
| "Accident" severity threshold | Not defined in source data |
