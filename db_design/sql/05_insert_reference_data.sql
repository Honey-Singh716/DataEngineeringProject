-- =============================================================
-- ROAD INSIGHT — PostgreSQL Database
-- File: 05_insert_reference_data.sql
-- Purpose: Insert all reference/dimension data
-- Run after: 04_create_indexes.sql
-- =============================================================

SET search_path TO road_insight, public;

-- =============================================================
-- SECTION 1: DATA SOURCES
-- =============================================================

INSERT INTO data_sources (source_file, source_directory, description, report_year, data_year_min, data_year_max, geographic_scope, notes)
VALUES
    ('LargeCities.csv',         'Data/',     'Large city-level accident, killed, injured stats for 50 Indian cities', 2023, 2022, 2023, 'City',     'Source: MoRTH Road Accident Report 2023'),
    ('LargeCitiesVio.csv',      'Data/',     'Traffic violation causes for 50 large Indian cities',                  2023, 2023, 2023, 'City',     'Year ASSUMED 2023 — verify with source report. Source: MoRTH 2023'),
    ('RoadNoAcc.csv',           'Data/',     'National annual road accident summary 2019-2023',                      2023, 2019, 2023, 'National', 'Source: MoRTH Road Accident Report 2023'),
    ('RoadStateWiseAcc.csv',    'Data/',     'State-wise annual accident counts 2019-2023',                          2023, 2019, 2023, 'State',    'Source: MoRTH Road Accident Report 2023'),
    ('RoadStatewiseKilled.csv', 'Data/',     'State-wise annual persons killed 2019-2023',                           2023, 2019, 2023, 'State',    'Source: MoRTH Road Accident Report 2023'),
    ('RoadTypeColl.csv',        'Data/',     'National collision type breakdown 2022-2023',                           2023, 2022, 2023, 'National', 'Source: MoRTH Road Accident Report 2023'),
    ('RoadTypeViol.csv',        'Data/',     'National traffic violation cause breakdown 2022-2023',                  2023, 2022, 2023, 'National', 'Source: MoRTH Road Accident Report 2023'),
    ('RA2019_A1.csv',           'DataSets/', 'National historical accident stats 1970-2019 with rates',              2019, 1970, 2019, 'National', 'Source: MoRTH Road Accident Report 2019, Annexure 1'),
    ('RA2019_A45.csv',          'DataSets/', 'City-level accidents by weather condition 2019',                        2019, 2019, 2019, 'City',     'Source: MoRTH Road Accident Report 2019, Annexure 45'),
    ('RA2019_A48.csv',          'DataSets/', 'City-level accidents by road feature type 2019',                        2019, 2019, 2019, 'City',     'Source: MoRTH Road Accident Report 2019, Annexure 48')
ON CONFLICT DO NOTHING;

-- =============================================================
-- SECTION 2: STATES AND UNION TERRITORIES
-- Source: RoadStateWiseAcc.csv and RoadStatewiseKilled.csv
-- All 37 entries from source data
-- =============================================================

INSERT INTO states (state_name, state_type, is_active, notes)
VALUES
    -- States
    ('Andhra Pradesh',                     'State',           TRUE,  NULL),
    ('Arunachal Pradesh',                  'State',           TRUE,  NULL),
    ('Assam',                              'State',           TRUE,  NULL),
    ('Bihar',                              'State',           TRUE,  NULL),
    ('Chhattisgarh',                       'State',           TRUE,  NULL),
    ('Goa',                                'State',           TRUE,  NULL),
    ('Gujarat',                            'State',           TRUE,  NULL),
    ('Haryana',                            'State',           TRUE,  NULL),
    ('Himachal Pradesh',                   'State',           TRUE,  NULL),
    ('Jharkhand',                          'State',           TRUE,  NULL),
    ('Karnataka',                          'State',           TRUE,  NULL),
    ('Kerala',                             'State',           TRUE,  NULL),
    ('Madhya Pradesh',                     'State',           TRUE,  NULL),
    ('Maharashtra',                        'State',           TRUE,  NULL),
    ('Manipur',                            'State',           TRUE,  NULL),
    ('Meghalaya',                          'State',           TRUE,  NULL),
    ('Mizoram',                            'State',           TRUE,  NULL),
    ('Nagaland',                           'State',           TRUE,  NULL),
    ('Odisha',                             'State',           TRUE,  NULL),
    ('Punjab',                             'State',           TRUE,  NULL),
    ('Rajasthan',                          'State',           TRUE,  NULL),
    ('Sikkim',                             'State',           TRUE,  NULL),
    ('Tamil Nadu',                         'State',           TRUE,  NULL),
    ('Telangana',                          'State',           TRUE,  NULL),
    ('Tripura',                            'State',           TRUE,  NULL),
    ('Uttarakhand',                        'State',           TRUE,  NULL),
    ('Uttar Pradesh',                      'State',           TRUE,  NULL),
    ('West Bengal',                        'State',           TRUE,  NULL),
    -- Union Territories
    ('Andaman & Nicobar Islands',          'Union Territory', TRUE,  NULL),
    ('Chandigarh',                         'Union Territory', TRUE,  NULL),
    ('Dadra & Nagar Haveli and Daman & Diu','Union Territory',TRUE,  'Dadra & Nagar Haveli merged with Daman & Diu into a single UT in 2020. Source notation: "Dadra & Nagar Haveli*"'),
    ('Daman & Diu',                        'Union Territory', FALSE, 'Merged into Dadra & Nagar Haveli and Daman & Diu UT from 2020. Data available for 2019 only.'),
    ('Delhi',                              'Union Territory', TRUE,  NULL),
    ('Jammu & Kashmir',                    'Union Territory', TRUE,  'Source notation: "J & K #". Includes Ladakh for 2019 and 2020 data.'),
    ('Ladakh',                             'Union Territory', TRUE,  'Became separate UT in Oct 2019. Data separately reported from 2021. 2019-2020 data included under Jammu & Kashmir.'),
    ('Lakshadweep',                        'Union Territory', TRUE,  NULL),
    ('Puducherry',                         'Union Territory', TRUE,  NULL)
ON CONFLICT (state_name) DO NOTHING;

-- =============================================================
-- SECTION 3: CITIES
-- 50 large Indian cities from source data
-- state_id assigned where determinable
-- =============================================================

INSERT INTO cities (city_name, state_id)
VALUES
    ('Agra',                   (SELECT state_id FROM states WHERE state_name = 'Uttar Pradesh')),
    ('Ahmedabad',              (SELECT state_id FROM states WHERE state_name = 'Gujarat')),
    ('Allahabad (Prayagraj)',   (SELECT state_id FROM states WHERE state_name = 'Uttar Pradesh')),
    ('Amritsar',               (SELECT state_id FROM states WHERE state_name = 'Punjab')),
    ('Asansol Durgapur',       (SELECT state_id FROM states WHERE state_name = 'West Bengal')),
    ('Aurangabad',             (SELECT state_id FROM states WHERE state_name = 'Maharashtra')),
    ('Bengaluru',              (SELECT state_id FROM states WHERE state_name = 'Karnataka')),
    ('Bhopal',                 (SELECT state_id FROM states WHERE state_name = 'Madhya Pradesh')),
    ('Chandigarh',             (SELECT state_id FROM states WHERE state_name = 'Chandigarh')),
    ('Coimbatore',             (SELECT state_id FROM states WHERE state_name = 'Tamil Nadu')),
    ('Chennai',                (SELECT state_id FROM states WHERE state_name = 'Tamil Nadu')),
    ('Delhi',                  (SELECT state_id FROM states WHERE state_name = 'Delhi')),
    ('Dhanbad',                (SELECT state_id FROM states WHERE state_name = 'Jharkhand')),
    ('Faridabad',              (SELECT state_id FROM states WHERE state_name = 'Haryana')),
    ('Ghaziabad',              (SELECT state_id FROM states WHERE state_name = 'Uttar Pradesh')),
    ('Gwalior',                (SELECT state_id FROM states WHERE state_name = 'Madhya Pradesh')),
    ('Hyderabad',              (SELECT state_id FROM states WHERE state_name = 'Telangana')),
    ('Indore',                 (SELECT state_id FROM states WHERE state_name = 'Madhya Pradesh')),
    ('Jabalpur',               (SELECT state_id FROM states WHERE state_name = 'Madhya Pradesh')),
    ('Jaipur',                 (SELECT state_id FROM states WHERE state_name = 'Rajasthan')),
    ('Jamshedpur',             (SELECT state_id FROM states WHERE state_name = 'Jharkhand')),
    ('Jodhpur',                (SELECT state_id FROM states WHERE state_name = 'Rajasthan')),
    ('Kannur',                 (SELECT state_id FROM states WHERE state_name = 'Kerala')),
    ('Kanpur',                 (SELECT state_id FROM states WHERE state_name = 'Uttar Pradesh')),
    ('Kozhikode',              (SELECT state_id FROM states WHERE state_name = 'Kerala')),
    ('Kochi',                  (SELECT state_id FROM states WHERE state_name = 'Kerala')),
    ('Kolkata',                (SELECT state_id FROM states WHERE state_name = 'West Bengal')),
    ('Kollam',                 (SELECT state_id FROM states WHERE state_name = 'Kerala')),
    ('Kota',                   (SELECT state_id FROM states WHERE state_name = 'Rajasthan')),
    ('Lucknow',                (SELECT state_id FROM states WHERE state_name = 'Uttar Pradesh')),
    ('Ludhiana',               (SELECT state_id FROM states WHERE state_name = 'Punjab')),
    ('Madurai',                (SELECT state_id FROM states WHERE state_name = 'Tamil Nadu')),
    ('Malappuram',             (SELECT state_id FROM states WHERE state_name = 'Kerala')),
    ('Meerut',                 (SELECT state_id FROM states WHERE state_name = 'Uttar Pradesh')),
    ('Mumbai',                 (SELECT state_id FROM states WHERE state_name = 'Maharashtra')),
    ('Nagpur',                 (SELECT state_id FROM states WHERE state_name = 'Maharashtra')),
    ('Nashik',                 (SELECT state_id FROM states WHERE state_name = 'Maharashtra')),
    ('Patna',                  (SELECT state_id FROM states WHERE state_name = 'Bihar')),
    ('Pune',                   (SELECT state_id FROM states WHERE state_name = 'Maharashtra')),
    ('Raipur',                 (SELECT state_id FROM states WHERE state_name = 'Chhattisgarh')),
    ('Rajkot',                 (SELECT state_id FROM states WHERE state_name = 'Gujarat')),
    ('Srinagar',               (SELECT state_id FROM states WHERE state_name = 'Jammu & Kashmir')),
    ('Surat',                  (SELECT state_id FROM states WHERE state_name = 'Gujarat')),
    ('Thiruvananthapuram',     (SELECT state_id FROM states WHERE state_name = 'Kerala')),
    ('Thrissur',               (SELECT state_id FROM states WHERE state_name = 'Kerala')),
    ('Tiruchirapalli',         (SELECT state_id FROM states WHERE state_name = 'Tamil Nadu')),
    ('Vadodara',               (SELECT state_id FROM states WHERE state_name = 'Gujarat')),
    ('Varanasi',               (SELECT state_id FROM states WHERE state_name = 'Uttar Pradesh')),
    ('Vijayawada',             (SELECT state_id FROM states WHERE state_name = 'Andhra Pradesh')),
    ('Visakhapatnam',          (SELECT state_id FROM states WHERE state_name = 'Andhra Pradesh'))
    -- NOTE: "Vizaq" in source mapped to Visakhapatnam — REQUIRES VERIFICATION
    -- NOTE: "Vadodra" in source = "Vadodara" (standardized)
    -- NOTE: "Khozikode" in source = "Kozhikode" (standardized)
    -- NOTE: "Mallapuram" in source = "Malappuram" (standardized)
    -- NOTE: "Thiruvanthapuram" in source = "Thiruvananthapuram" (standardized)
    -- NOTE: "Vijaywada city" in source = "Vijayawada" (standardized)
ON CONFLICT (city_name) DO NOTHING;

-- =============================================================
-- SECTION 4: WEATHER CONDITIONS
-- =============================================================

INSERT INTO weather_conditions (weather_condition_name, description)
VALUES
    ('Sunny/Clear',     'Clear or sunny weather with good visibility at time of accident'),
    ('Rainy',           'Rainy conditions at time of accident'),
    ('Foggy and Misty', 'Foggy or misty conditions with reduced visibility'),
    ('Hail/Sleet',      'Hail or sleet conditions at time of accident'),
    ('Others',          'Weather conditions not classified in the above categories')
ON CONFLICT (weather_condition_name) DO NOTHING;

-- =============================================================
-- SECTION 5: ROAD FEATURES
-- =============================================================

INSERT INTO road_features (road_feature_name, description)
VALUES
    ('Straight Road',                    'Accident occurred on a straight road section'),
    ('Curved Road',                      'Accident occurred on a curved road section'),
    ('Bridge',                           'Accident occurred on a bridge'),
    ('Culvert',                          'Accident occurred at or near a culvert'),
    ('Pot Holes',                        'Accident occurred at a location with pot holes'),
    ('Steep Grade',                      'Accident occurred on a steep gradient/grade road'),
    ('Ongoing Road Works/Under Construction', 'Accident occurred in a road construction zone'),
    ('Others',                           'Road feature not classified in the above categories')
ON CONFLICT (road_feature_name) DO NOTHING;

-- =============================================================
-- SECTION 6: COLLISION TYPES
-- =============================================================

INSERT INTO collision_types (collision_type_name, description)
VALUES
    ('Hit and Run',        'Accident where the offending vehicle fled the scene'),
    ('With parked Vehicle','Collision with a parked vehicle'),
    ('Hit from Back',      'Rear-end collision — vehicle struck from behind'),
    ('Hit from side',      'Side impact collision'),
    ('Run off Road',       'Vehicle left the roadway'),
    ('Fixed object',       'Collision with a fixed roadside object'),
    ('Vehicle overturn',   'Vehicle rolled or overturned'),
    ('Head on collision',  'Front-to-front collision between two vehicles'),
    ('Others',             'Collision type not classified in the above categories')
ON CONFLICT (collision_type_name) DO NOTHING;

-- =============================================================
-- SECTION 7: VIOLATION TYPES
-- =============================================================

INSERT INTO violation_types (violation_type_name, description)
VALUES
    ('Over-speeding',                                    'Accident caused by driving above the permissible speed limit'),
    ('Drunken driving/consumption of alcohol & drug',    'Accident caused by driving under influence of alcohol or drugs'),
    ('Driving on wrong side/Lane indiscipline',          'Accident caused by driving on wrong side of road or lane indiscipline'),
    ('Jumping red light',                                'Accident caused by violating red traffic signal'),
    ('Use of mobile phone',                              'Accident caused by use of mobile phone while driving'),
    ('Others',                                           'Traffic violation not classified in the above categories')
ON CONFLICT (violation_type_name) DO NOTHING;
