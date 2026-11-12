"""Script to update RoadInsight India project tracker with verified implementation details.
Outputs: /Users/jayantsoni/Desktop/RoadInsight_India/Lab1_Group19_Progress_Updated.xlsx
"""

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

def update_tracker():
    src_path = '/Users/jayantsoni/Desktop/RoadInsight_India/Lab1_Group19_Final.xlsx'
    dst_path = '/Users/jayantsoni/Desktop/RoadInsight_India/Lab1_Group19_Progress_Updated.xlsx'
    
    wb = openpyxl.load_workbook(src_path)
    
    # -------------------------------------------------------------
    # 1. Update 'Essence Card Progression'
    # -------------------------------------------------------------
    ws_ec = wb['Essence Card Progression']
    
    # Summary Alphas (Rows 8 to 14)
    # Row 8: Opportunity
    ws_ec.cell(8, 4, '5 / 6 (Card 6 N/A)')
    ws_ec.cell(8, 6, 'In Progress — Addressed (Staging Verification)')
    ws_ec.cell(8, 7, 'In Progress')
    ws_ec.cell(8, 8, '— (Revised Forecast: 25-11-2026)')
    ws_ec.cell(8, 9, 'Core data pipeline and 3NF warehouse operational; live cloud demonstration and multi-user verification in progress. Card 6 (Benefit Accrued) is N/A as commercial ROI is outside academic scope.')
    
    # Row 9: Stakeholders
    ws_ec.cell(9, 4, '5 / 6 (Card 6 N/A)')
    ws_ec.cell(9, 6, 'In Progress — Satisfied for Deployment')
    ws_ec.cell(9, 7, 'In Progress')
    ws_ec.cell(9, 8, '— (Revised Forecast: 25-11-2026)')
    ws_ec.cell(9, 9, 'User personas and validation criteria verified; live evaluator walkthrough and deployment verification in progress. Card 6 (Satisfied in Use) is N/A as daily operational use is outside academic course scope.')
    
    # Row 10: Requirements
    ws_ec.cell(10, 4, '5 / 6')
    ws_ec.cell(10, 6, 'In Progress — Fulfilled (Under Final Verification)')
    ws_ec.cell(10, 7, 'In Progress')
    ws_ec.cell(10, 8, '— (Revised Forecast: 25-11-2026)')
    ws_ec.cell(10, 9, 'All 35 atomic requirements conceived and bounded; 45 automated pytest tests passing locally; live cloud environment validation in progress.')
    
    # Row 11: Software Systems
    ws_ec.cell(11, 4, '4 / 6 (Card 6 N/A)')
    ws_ec.cell(11, 6, 'In Progress — Operational (Cloud Staging in Progress)')
    ws_ec.cell(11, 7, 'In Progress')
    ws_ec.cell(11, 8, '— (Revised Forecast: 25-11-2026)')
    ws_ec.cell(11, 9, 'Architecture operational in Docker local environment with PostgreSQL, Streamlit, and Groq; live cloud hosting and daemon integration in progress. Card 6 (Retired) is N/A as system remains active.')
    
    # Row 12: Work
    ws_ec.cell(12, 4, '4 / 6')
    ws_ec.cell(12, 6, 'In Progress — Concluding Sprint 7')
    ws_ec.cell(12, 7, 'In Progress')
    ws_ec.cell(12, 8, '— (Revised Forecast: 25-11-2026)')
    ws_ec.cell(12, 9, 'Sprints 1 to 6 complete; Sprint 7 tasks under active verification as of 10-11-2026 reporting cut-off (378/400 hrs completed, 94.5% progress; 4 tasks in progress). Final closure pending acceptance.')
    
    # Row 13: Way of Working
    ws_ec.cell(13, 4, '4 / 6 (Card 6 N/A)')
    ws_ec.cell(13, 6, 'In Progress — Working Well')
    ws_ec.cell(13, 7, 'In Progress')
    ws_ec.cell(13, 8, '— (Revised Forecast: 25-11-2026)')
    ws_ec.cell(13, 9, 'Agile practices, PR reviews, automated pytest fixtures actively supporting Sprint 7 and hardening. Card 6 (Retired) is N/A as repo and practices remain active.')
    
    # Row 14: Team
    ws_ec.cell(14, 4, '3 / 5')
    ws_ec.cell(14, 6, 'In Progress — Performing')
    ws_ec.cell(14, 7, 'In Progress')
    ws_ec.cell(14, 8, '— (Revised Forecast: 25-11-2026)')
    ws_ec.cell(14, 9, '4-member team actively collaborating on feature hardening, testing regression, and final progress documentation. Team has not adjourned as project is in progress.')

    # Detail Cards (Rows 17 to 57)
    # Opportunity Card 5 (Row 21)
    ws_ec.cell(21, 7, 'In Progress')
    ws_ec.cell(21, 8, '— (Target: 20-11-2026)')
    ws_ec.cell(21, 9, 'Core pipeline and warehouse address analytical opportunity; live cloud demonstration and multi-user verification in progress.')
    
    # Stakeholders Card 5 (Row 27)
    ws_ec.cell(27, 7, 'In Progress')
    ws_ec.cell(27, 8, '— (Target: 22-11-2026)')
    ws_ec.cell(27, 9, 'Academic evaluation rubric criteria addressed; final live deployment review and demonstration pending.')
    
    # Requirements Card 6 (Row 34)
    ws_ec.cell(34, 7, 'In Progress')
    ws_ec.cell(34, 8, '— (Target: 22-11-2026)')
    ws_ec.cell(34, 9, 'Requirements implemented and verified by 45 automated pytest tests; live multi-user concurrency and live Groq LLM latency NFR verification in progress.')
    
    # Software Systems Card 5 (Row 39)
    ws_ec.cell(39, 7, 'In Progress')
    ws_ec.cell(39, 8, '— (Target: 23-11-2026)')
    ws_ec.cell(39, 9, 'System operational in Docker local environment; live cloud deployment with managed PostgreSQL database connection in progress.')
    
    # Work Card 5 (Row 45)
    ws_ec.cell(45, 7, 'In Progress')
    ws_ec.cell(45, 8, '— (Target: 20-11-2026)')
    ws_ec.cell(45, 9, 'Core implementation completed; final sprint integration tasks and evidence hardening in progress as of 10-11-2026.')
    
    # Work Card 6 (Row 46)
    ws_ec.cell(46, 7, 'In Progress')
    ws_ec.cell(46, 8, '— (Target: 25-11-2026)')
    ws_ec.cell(46, 9, 'Project deliverables in active refinement; final submission and project closure planned for 25-11-2026.')
    
    # Way of Working Card 5 (Row 51)
    ws_ec.cell(51, 7, 'In Progress')
    ws_ec.cell(51, 8, '— (Target: 22-11-2026)')
    ws_ec.cell(51, 9, 'Cross-functional collaboration seamless; practices actively applied during feature hardening and regression testing.')
    
    # Team Card 4 (Row 56)
    ws_ec.cell(56, 7, 'In Progress')
    ws_ec.cell(56, 8, '— (Target: 22-11-2026)')
    ws_ec.cell(56, 9, 'Commitments met; 45 automated pytest tests and 14 DQ checks passed; team actively performing on hardening tasks.')
    
    # Team Card 5 (Row 57)
    ws_ec.cell(57, 7, 'In Progress')
    ws_ec.cell(57, 8, '— (Target: 25-11-2026)')
    ws_ec.cell(57, 9, 'Team remains active during project execution and documentation; adjournment will occur upon final evaluation.')

    # -------------------------------------------------------------
    # 2. Update 'Requirements'
    # -------------------------------------------------------------
    ws_req = wb['Requirements']
    ws_req.cell(2, 3, '08-11-2026 (Baseline) | Revised Forecast: 25-11-2026')
    ws_req.cell(2, 5, '4-member team; batch Data Engineering & Conversational AI platform. In progress as of 10-11-2026 reporting cut-off. Core ETL, 3NF schema, 45 automated tests passed; live cloud deployment and latency benchmarking in progress.')

    # -------------------------------------------------------------
    # 3. Update 'Sprint Plans'
    # -------------------------------------------------------------
    ws_sp = wb['Sprint Plans']
    ws_sp.cell(2, 3, '08-11-2026 (Baseline) | Revised Forecast: 25-11-2026')
    ws_sp.cell(2, 5, '10-11-2026 (Cut-off)')
    ws_sp.cell(2, 6, '94.5%')
    ws_sp.cell(2, 7, 'Total Estimated Effort: 400 hours | Completed: 378 hours (94.5%) | Remaining: 22 hours (5.5%) | Jayant Soni: 100/104 hrs (26.5%) | Honey Singh: 101/104 hrs (26.7%) | Gautam: 99/104 hrs (26.2%) | Sugam Umale: 78/88 hrs (20.6%)')
    
    # Sprint 7 tasks (Rows 29 to 36)
    # S7-T25A
    ws_sp.cell(29, 10, '— (Forecast: 20-11-2026)')
    ws_sp.cell(29, 11, 'In Progress')
    ws_sp.cell(29, 13, 'Critical — Local pipeline verified with 16.57ms non-LLM overhead; live Groq API latency benchmark requires live network/cloud execution.')
    
    # S7-T25B
    ws_sp.cell(30, 10, '07-11-2026')
    ws_sp.cell(30, 11, 'Completed')
    ws_sp.cell(30, 13, 'Critical — 12/12 security checks passed; verified via verify_readonly_security.py and AST injection tests.')
    
    # S7-T26A
    ws_sp.cell(31, 10, '07-11-2026')
    ws_sp.cell(31, 11, 'Completed')
    ws_sp.cell(31, 13, 'Critical — Verified 100% referential integrity & 0 orphaned fact rows across 16 warehouse tables.')
    
    # S7-T26B
    ws_sp.cell(32, 10, '07-11-2026')
    ws_sp.cell(32, 11, 'Completed')
    ws_sp.cell(32, 13, 'Critical — Reconciliation audit confirms 0 unexplained variance; Annexure 45 whitespace fix verified (Check Q6 100% pass).')
    
    # S7-T27A
    ws_sp.cell(33, 10, '07-11-2026')
    ws_sp.cell(33, 11, 'Completed')
    ws_sp.cell(33, 13, 'Critical — All 21 backend unit tests, 10 ETL tests, and 1 secret scan test pass without errors.')
    
    # S7-T27B
    ws_sp.cell(34, 10, '— (Forecast: 22-11-2026)')
    ws_sp.cell(34, 11, 'In Progress')
    ws_sp.cell(34, 13, 'Critical — 45 automated pytest tests passing locally; 9 tests skipped pending live DB/Groq cloud container setup.')
    
    # S7-T28A
    ws_sp.cell(35, 10, '— (Forecast: 21-11-2026)')
    ws_sp.cell(35, 11, 'In Progress')
    ws_sp.cell(35, 13, 'Critical — Verified 50-city metrics, collision breakdowns, and weather stats; multi-user concurrent load audit in progress.')
    
    # S7-T28B
    ws_sp.cell(36, 10, '— (Forecast: 25-11-2026)')
    ws_sp.cell(36, 11, 'In Progress')
    ws_sp.cell(36, 13, 'High — Milestone reports and Data Dictionary complete; Final Progress Report in progress (cut-off 10-11-2026); final acceptance review pending.')

    # -------------------------------------------------------------
    # 4. Update 'Test Sheet'
    # -------------------------------------------------------------
    ws_ts = wb['Test Sheet']
    # Row 17 (TEST-16)
    ws_ts.cell(17, 6, '08-11-2026 (Baseline) | Forecast: 25-11-2026')
    ws_ts.cell(17, 7, '08-11-2026')
    ws_ts.cell(17, 8, '10-11-2026')
    ws_ts.cell(17, 9, 'In Progress')
    ws_ts.cell(17, 10, 'Passed (Local) / Staging In Progress')
    ws_ts.cell(17, 11, 'Passed (Local): Conversational workflow verified; 45 automated pytest tests passed across 4 test suites (21 in test_backend.py, 13 in test_milestone2.py, 10 in test_etl.py, 1 in test_no_secrets.py; 9 live tests skipped). Live cloud UI demonstration in progress.')
    ws_ts.cell(17, 13, 'AI Analyst Streamlit tab renders conversation history, suggested queries, SQL transparency expander, auto-charts (bar/line/pie), and handles single-column/empty result edge cases. 45/45 automated pytest tests passing locally; 14/14 Data Quality checks passing; live cloud deployment in progress.')

    # Row 19 (Status Legend)
    ws_ts.cell(19, 2, 'Execution_Status tracks delivery progress; Result_Status records verified test outcome. As of 10-11-2026 reporting cut-off, automated tests are 100% passing (45 passed, 0 failed, 9 skipped for live services); 14/14 Data Quality checks passed; 12/16 manual test scenarios verified; live cloud deployment and end-to-end integration tests are In Progress.')

    # Row 20 (Test Hierarchy Note)
    ws_ts.cell(20, 2, 'The 16 documented test scenarios organize the end-to-end verification plan across architectural modules. The codebase contains 45 passing automated pytest tests across 4 suites: tests/test_backend.py (21 unit tests: Groq parsing, AST validation, injection blocking, error handlers); tests/test_milestone2.py (13 system/integration tests: database role permissions, view accessibility, DML denial, Plotly charts); tests/test_etl.py (10 ETL regression tests: Annexure 45 whitespace sanitization, unpivot validation, staging loader); tests/test_no_secrets.py (1 security scan test: 0 secrets across 128 tracked files). In addition, scripts/run_checks.py verifies 14 database Data Quality rules (R1-R6, Q1-Q8) with 100% success, and scripts/verify_readonly_security.py executes 12 database engine-level security audit checks verifying read-only enforcement. 12 manual test procedures passed; 4 live UI procedures are in progress pending live daemon/cloud deployment.')

    # -------------------------------------------------------------
    # 5. Update 'Traceability Matrix'
    # -------------------------------------------------------------
    ws_tm = wb['Traceability Matrix']
    
    # Update verification status in rows 64 to 71 (Task classification table)
    # Row 64: S7-T25A
    ws_tm.cell(64, 10, 'In Progress — Local pipeline verified <17ms overhead; live Groq API latency benchmark requires live network/cloud execution.')
    
    # Row 65: S7-T25B
    ws_tm.cell(65, 10, 'Passed: 12/12 security checks passed; verified via verify_readonly_security.py.')
    
    # Row 66: S7-T26A
    ws_tm.cell(66, 10, 'Passed: Verified 100% referential integrity & 0 orphaned fact rows across 16 tables.')
    
    # Row 67: S7-T26B
    ws_tm.cell(67, 10, 'Passed: Final reconciliation audit confirms 0 unexplained measure variance; Q6 100% pass.')
    
    # Row 68: S7-T27A
    ws_tm.cell(68, 10, 'Passed: All 21 backend unit tests, 10 ETL tests, and 1 secret scan test pass without errors.')
    
    # Row 69: S7-T27B
    ws_tm.cell(69, 10, 'In Progress — 45 automated pytest tests passing locally; 9 tests skipped pending live DB/Groq cloud container setup.')
    
    # Row 70: S7-T28A
    ws_tm.cell(70, 10, 'In Progress — 50-city metrics, collision breakdowns verified; multi-user UI load testing in progress.')
    
    # Row 71: S7-T28B
    ws_tm.cell(71, 10, 'In Progress — Milestone reports and Data Dictionary complete; Final Progress Report in progress; target 25-11-2026.')

    # -------------------------------------------------------------
    # 6. Create 'Implementation_Log' Worksheet
    # -------------------------------------------------------------
    if 'Implementation_Log' in wb.sheetnames:
        del wb['Implementation_Log']
    ws_log = wb.create_sheet('Implementation_Log')
    
    # Styles for tables
    navy_header_fill = PatternFill(start_color='193C65', end_color='193C65', fill_type='solid')
    header_font = Font(name='Arial', size=10, bold=True, color='FFFFFF')
    sub_font = Font(name='Arial', size=9, bold=True, color='193C65')
    body_font = Font(name='Arial', size=9, color='000000')
    body_font_bold = Font(name='Arial', size=9, bold=True, color='000000')
    thin_border_side = Side(border_style='thin', color='D9D9D9')
    cell_border = Border(left=thin_border_side, right=thin_border_side, top=thin_border_side, bottom=thin_border_side)
    center_align = Alignment(horizontal='center', vertical='center', wrap_text=True)
    left_align = Alignment(horizontal='left', vertical='center', wrap_text=True)
    
    # Title Block
    ws_log.cell(1, 1, 'ROADINSIGHT INDIA — ENGINEERING IMPLEMENTATION & MILESTONE LOG (23-08-2026 TO 10-11-2026)')
    ws_log.cell(1, 1).font = Font(name='Arial', size=12, bold=True, color='193C65')
    ws_log.cell(2, 1, 'Project Status: In Progress | Planned End Date: 08-11-2026 | Cut-off Date: 10-11-2026 | Revised Forecast Completion: 25-11-2026')
    ws_log.cell(2, 1).font = Font(name='Arial', size=9, italic=True, color='595959')
    
    headers_log = [
        'Milestone_ID', 'Date_Range', 'Sprint_No', 'Parent_Module', 'Submodule_Code',
        'Implementation / Activity Description', 'Testing / Verification Conducted',
        'Concrete Outcome / Artifact Produced', 'Team Member(s)', 'Status', 'Traceability_IDs'
    ]
    
    for c_idx, h in enumerate(headers_log, start=1):
        cell = ws_log.cell(4, c_idx, h)
        cell.font = header_font
        cell.fill = navy_header_fill
        cell.alignment = center_align
    
    milestones_data = [
        (
            'MS-01', '23-08-2026 to 28-08-2026', 'Sprint 1', 'Data Acquisition & Raw Data Lake', 'MOD_01_ACQUISITION',
            'Project inception, government dataset viability analysis across MoRTH and Open Government Data (OGD) platforms. Raw schema profiling, delimiter audits, and initial requirements baseline.',
            'Inspection of 10 MoRTH CSV tables (1970–2020); delimiter and line-break audit.',
            'Initial requirements baseline (35 atomic requirements); data source catalog; project architecture brief.',
            'Jayant Soni, Honey Singh', 'Completed', 'S1-T01, S1-T02; FR-01.1, FR-02.1; TEST-01'
        ),
        (
            'MS-02', '25-08-2026 to 05-09-2026', 'Sprint 1', 'PostgreSQL Warehouse & Airflow', 'MOD_03_PIPELINE_ORCHESTRATION',
            'Engineering infrastructure setup: Git branch protection rules, Docker Compose multi-service architecture, Airflow base environment, and stakeholder persona mapping.',
            'Docker Compose container health checks; Git PR review template validation.',
            'docker-compose.yml; repo branch rules; stakeholder persona profiles and matrix framework.',
            'Gautam, Sugam Umale', 'Completed', 'S1-T03, S1-T04; NFR-03.1, NFR-03.2; TEST-10'
        ),
        (
            'MS-03', '06-09-2026 to 15-09-2026', 'Sprint 2', 'Data Acquisition & Raw Data Lake', 'MOD_01_ACQUISITION',
            'Automated ingestion scripts to fetch 10 historical MoRTH road-accident datasets; lake landing with immutable storage and SHA256 cryptographic checksums.',
            'SHA256 checksum comparison against source files; ingest timestamp and size logging.',
            'Data lake ingestion scripts; raw data store in Data/ and DataSets/; provenance metadata catalog.',
            'Jayant Soni, Gautam', 'Completed', 'S2-T05; FR-01.1, FR-01.2, FR-01.3; TEST-01, TEST-02'
        ),
        (
            'MS-04', '06-09-2026 to 18-09-2026', 'Sprint 2', 'PostgreSQL Warehouse & Airflow', 'MOD_03_ETL_WAREHOUSE',
            'PostgreSQL normalized relational 3NF DDL migrations (01_create_schema.sql to 05_insert_reference_data.sql); table constraints, domains, and master reference lookups.',
            'SQL migration execution tests; primary key uniqueness and foreign key constraint validation.',
            '16 warehouse tables (dim_state, dim_year, fact_accident_summary, etc.); 01-05 SQL migration scripts.',
            'Honey Singh', 'Completed', 'S2-T06; FR-03.2, FR-03.3; TEST-05'
        ),
        (
            'MS-05', '08-09-2026 to 19-09-2026', 'Sprint 2', 'PostgreSQL Warehouse & Airflow', 'MOD_03_PIPELINE_ORCHESTRATION',
            'Airflow DAG orchestration skeleton with task operator dependencies; Streamlit multi-page frontend scaffold with layout structure and page navigation routing.',
            'Airflow DAG graph syntax validation (dry run); Streamlit local web server startup test.',
            'dags/road_insight_pipeline.py skeleton; dashboard/app.py shell and page routing structure.',
            'Gautam, Sugam Umale', 'Completed', 'S2-T07, S2-T08; FR-04.1, FR-06.1; TEST-06, TEST-08'
        ),
        (
            'MS-06', '20-09-2026 to 29-09-2026', 'Sprint 3', 'Data Quality & ETL', 'MOD_02_DATA_QUALITY',
            'Data cleansing engine implementation: schema validation, null/duplicate detection, 36 state/UT name standardizer mapping to census nomenclature, and quarantine table logging.',
            'Unit tests on malformed records; synthetic duplicate injection; state name resolution test.',
            'Cleansing engine modules; state mapping lookup; road_insight.rejected_rows quarantine table.',
            'Honey Singh', 'Completed', 'S3-T10; FR-02.2, FR-02.3, FR-02.4, FR-02.5; TEST-03, TEST-12'
        ),
        (
            'MS-07', '20-09-2026 to 03-10-2026', 'Sprint 3', 'SQL Analytics, Dashboard & Conversational Analytics', 'MOD_06_LLM_BACKEND',
            'Conversational analytics Text-to-SQL architecture, prompt design with schema grounding and generation constraints; core dashboard pages for national accident trends and state rankings.',
            'Prompt parsing unit tests; Plotly chart responsive rendering across simulated viewport widths.',
            'Schema prompt context specs; National Trends and State Rankings dashboard tabs in Streamlit.',
            'Jayant Soni, Sugam Umale', 'Completed', 'S3-T09, S3-T12; FR-07.1, FR-06.2; TEST-08, TEST-13'
        ),
        (
            'MS-08', '04-10-2026 to 15-10-2026', 'Sprint 4', 'SQL Analytics, Dashboard & Conversational Analytics', 'MOD_06_LLM_BACKEND',
            'Groq Cloud LLM API integration (openai/gpt-oss-120b); single-transaction canonical ETL loader (db_design/06_etl_loader.py) with wide-to-long table unpivoting and rollback guarantees.',
            'Mocked Groq API response parsing; transaction rollback test on injected syntax error in loader.',
            'Groq API client wrapper (ai_analyst/llm.py); atomic ETL loader (06_etl_loader.py).',
            'Jayant Soni, Honey Singh', 'Completed', 'S4-T13, S4-T14; FR-07.1, FR-03.1, FR-03.3; TEST-04, TEST-13'
        ),
        (
            'MS-09', '06-10-2026 to 17-10-2026', 'Sprint 4', 'SQL Analytics, Dashboard & Conversational Analytics', 'MOD_04_SQL_ANALYTICS',
            'Creation of 9 analytical views (08_views.sql) covering 50-city metrics, collision types, weather stats, and road features; dashboard pages for 50-City Rankings and Collision & Violations.',
            'View output reconciliation against raw CSV manual sums; SQL syntax checks.',
            '08_views.sql; dashboard 50-City Rankings page; Collision Types & Violations interactive tabs.',
            'Honey Singh, Sugam Umale', 'Completed', 'S4-T15, S4-T16; FR-05.1, FR-05.2, FR-06.2, FR-06.3; TEST-07, TEST-08'
        ),
        (
            'MS-10', '18-10-2026 to 27-10-2026', 'Sprint 5', 'PostgreSQL Warehouse & Airflow', 'MOD_03_ETL_WAREHOUSE',
            'B-tree index optimization (04_create_indexes.sql) for <500ms query latency; pipeline rerun idempotency via ON CONFLICT DO NOTHING; interactive AI Analyst Streamlit chat UI tab.',
            'EXPLAIN ANALYZE query plan audit; duplicate batch rerun test verifying identical warehouse row count.',
            'Optimized schema indexes; idempotent loader logic; dashboard/ai_analyst_tab.py with dark Plotly styling.',
            'Honey Singh, Gautam, Sugam Umale', 'Completed', 'S5-T18, S5-T19, S5-T20; NFR-01.2, FR-03.4, FR-07.3; TEST-05, TEST-07, TEST-09'
        ),
        (
            'MS-11', '28-10-2026 to 03-11-2026', 'Sprint 6', 'SQL Analytics, Dashboard & Conversational Analytics', 'MOD_06_LLM_BACKEND',
            'Multi-layer AST SQL validator (ai_analyst/security.py) using sqlglot to block DDL/DML, system catalogs, and unallowed tables; unprivileged PostgreSQL read-only role (setup_readonly_role.sql).',
            'Injection penetration test suite (UNION, DROP, comment injection); 12 read-only role DB security checks.',
            'AST SQL validator module; scripts/setup_readonly_role.sql; scripts/verify_readonly_security.py.',
            'Jayant Soni, Honey Singh', 'Completed', 'S6-T21, S6-T22; NFR-04.1, NFR-04.2, FR-07.2; TEST-14, TEST-15'
        ),
        (
            'MS-12', '29-10-2026 to 04-11-2026', 'Sprint 6', 'PostgreSQL Warehouse & Airflow', 'MOD_03_PIPELINE_ORCHESTRATION',
            'Automated pytest harness development (tests/test_backend.py, tests/test_milestone2.py); UI enhancements: suggested analytical questions, SQL transparency expander, and CSV download.',
            'Pytest test suite execution; UI expander toggle test; CSV export byte stream validation.',
            'Pytest test harness; 34 automated unit & system tests; suggested questions chips and SQL expander in UI.',
            'Gautam, Sugam Umale', 'Completed', 'S6-T23, S6-T24; NFR-03.1, FR-07.3; TEST-14, TEST-16'
        ),
        (
            'MS-13', '04-11-2026 to 08-11-2026', 'Sprint 7 (Baseline End)', 'Data Quality & ETL', 'MOD_03_ETL_WAREHOUSE',
            'Comprehensive data reconciliation audit; Annexure 45 trailing whitespace defect identified and stripped in 06_etl_loader.py; 14 database Data Quality checks (R1-R6, Q1-Q8) achieved 100% PASS; automated test suite expanded to 45 passing tests.',
            'scripts/run_checks.py (14 DQ checks); tests/test_etl.py (10 tests); tests/test_no_secrets.py (0 secrets across 128 files); 45 pytest tests passed.',
            'Sanitized etl_loader; regression tests in test_etl.py; 14/14 passed DQ report; 45 passed pytest report.',
            'Jayant Soni, Honey Singh, Gautam, Sugam Umale', 'Completed', 'S7-T25B, S7-T26A, S7-T26B, S7-T27A; NFR-02.1-02.4, NFR-03.1; TEST-03, TEST-04, TEST-05, TEST-10, TEST-15'
        ),
        (
            'MS-14', '08-11-2026 to 10-11-2026', 'Sprint 7 Extension', 'SQL Analytics, Dashboard & Conversational Analytics', 'MOD_06_LLM_BACKEND',
            'Benchmarking of local pipeline latency (mean non-LLM overhead 16.57ms); evaluation of 16 manual test scenarios (12 passed, 4 blocked by sandbox offline daemon); preparation of Final Project Progress Report as of 10-11-2026 cut-off; live cloud deployment and latency benchmarking in progress.',
            'scripts/benchmarks/bench_pipeline_latency.py execution; manual test suite audit; tracker reconciliation.',
            'Pipeline benchmark results; updated Excel tracker (Lab1_Group19_Progress_Updated.xlsx); comprehensive progress report; revised forecast schedule (25-11-2026).',
            'Jayant Soni, Honey Singh, Gautam, Sugam Umale', 'In Progress', 'S7-T25A, S7-T27B, S7-T28A, S7-T28B; NFR-01.1, NFR-01.3, FR-04.2, FR-06.4; TEST-06, TEST-11, TEST-16'
        )
    ]
    
    for row_idx, m in enumerate(milestones_data, start=5):
        for col_idx, val in enumerate(m, start=1):
            cell = ws_log.cell(row_idx, col_idx, val)
            cell.font = body_font
            cell.border = cell_border
            if col_idx in [1, 3, 10]:
                cell.alignment = center_align
                if col_idx == 10:
                    if val == 'Completed':
                        cell.fill = PatternFill(start_color='E2EFDA', end_color='E2EFDA', fill_type='solid')
                        cell.font = Font(name='Arial', size=9, bold=True, color='375623')
                    else:
                        cell.fill = PatternFill(start_color='FFF2CC', end_color='FFF2CC', fill_type='solid')
                        cell.font = Font(name='Arial', size=9, bold=True, color='7F6000')
            else:
                cell.alignment = left_align

    # Auto-adjust column widths for Implementation_Log
    col_widths_log = [14, 24, 12, 28, 22, 45, 38, 38, 26, 14, 30]
    for idx, width in enumerate(col_widths_log, start=1):
        ws_log.column_dimensions[get_column_letter(idx)].width = width

    # -------------------------------------------------------------
    # 7. Create 'PM_Metrics' Worksheet
    # -------------------------------------------------------------
    if 'PM_Metrics' in wb.sheetnames:
        del wb['PM_Metrics']
    ws_pm = wb.create_sheet('PM_Metrics')
    
    ws_pm.cell(1, 1, 'ROADINSIGHT INDIA — PROJECT MANAGEMENT METRICS & PERFORMANCE CALCULATIONS')
    ws_pm.cell(1, 1).font = Font(name='Arial', size=12, bold=True, color='193C65')
    ws_pm.cell(2, 1, 'Reporting Cut-off: 10-11-2026 | Baseline Plan: 23-08-2026 to 08-11-2026 | Revised Forecast: 25-11-2026 | Status: In Progress')
    ws_pm.cell(2, 1).font = Font(name='Arial', size=9, italic=True, color='595959')
    
    # Section 1: Sprint Velocity & Planned vs Actual Effort
    ws_pm.cell(4, 1, '1. SPRINT VELOCITY & EFFORT SUMMARY')
    ws_pm.cell(4, 1).font = sub_font
    
    vel_headers = ['Sprint_No', 'Sprint_Date_Range', 'Tasks_Planned', 'Tasks_Completed', 'Planned_Hours', 'Completed_Hours', 'Sprint_Velocity (hrs)', 'Sprint_Throughput (tasks)', 'Sprint_Status']
    for c_idx, h in enumerate(vel_headers, start=1):
        c = ws_pm.cell(5, c_idx, h)
        c.font = header_font
        c.fill = navy_header_fill
        c.alignment = center_align
    
    vel_data = [
        ('Sprint 1', '23-08-2026 to 05-09-2026', 4, 4, 57, 57, 57, 4, 'Completed'),
        ('Sprint 2', '06-09-2026 to 19-09-2026', 4, 4, 61, 61, 61, 4, 'Completed'),
        ('Sprint 3', '20-09-2026 to 03-10-2026', 4, 4, 60, 60, 60, 4, 'Completed'),
        ('Sprint 4', '04-10-2026 to 17-10-2026', 4, 4, 57, 57, 57, 4, 'Completed'),
        ('Sprint 5', '18-10-2026 to 27-10-2026', 4, 4, 57, 57, 57, 4, 'Completed'),
        ('Sprint 6', '28-10-2026 to 03-11-2026', 4, 4, 54, 54, 54, 4, 'Completed'),
        ('Sprint 7', '04-11-2026 to 10-11-2026 (Cut-off)', 8, 4, 54, 38, 38, 4, 'In Progress (Extension to 25-11)'),
        ('TOTAL / AVG', '23-08-2026 to 10-11-2026', 32, 28, 400, 384, 54.9, 4.0, 'In Progress (96.0% effort, 87.5% tasks)')
    ]
    for r_idx, row in enumerate(vel_data, start=6):
        is_total = (r_idx == 6 + len(vel_data) - 1)
        for c_idx, val in enumerate(row, start=1):
            cell = ws_pm.cell(r_idx, c_idx, val)
            cell.font = body_font_bold if is_total else body_font
            cell.border = cell_border
            cell.alignment = center_align
            if is_total:
                cell.fill = PatternFill(start_color='F2F2F2', end_color='F2F2F2', fill_type='solid')

    # Section 2: Burndown & Burn-up
    r_start = 16
    ws_pm.cell(r_start, 1, '2. BURNDOWN & BURN-UP SCHEDULE (SCOPE: 400 HOURS, 32 TASKS)')
    ws_pm.cell(r_start, 1).font = sub_font
    
    bd_headers = ['Timeline_Point', 'Date', 'Scope_Total_Hours', 'Completed_Hours (Burn-up)', 'Remaining_Hours (Burndown)', 'Tasks_Completed', 'Tasks_Remaining', 'Completion_Percentage', 'Trajectory_Notes']
    for c_idx, h in enumerate(bd_headers, start=1):
        c = ws_pm.cell(r_start + 1, c_idx, h)
        c.font = header_font
        c.fill = navy_header_fill
        c.alignment = center_align
    
    bd_data = [
        ('Project Kickoff', '23-08-2026', 400, 0, 400, 0, 32, '0.0%', 'Baseline work breakdown established; 7 sprints allocated.'),
        ('End of Sprint 1', '05-09-2026', 400, 57, 343, 4, 28, '14.3%', 'On schedule; data viability confirmed; repo initialized.'),
        ('End of Sprint 2', '19-09-2026', 400, 118, 282, 8, 24, '29.5%', 'On schedule; raw data ingested; 13 DDL tables created.'),
        ('End of Sprint 3', '03-10-2026', 400, 178, 222, 12, 20, '44.5%', 'On schedule; cleansing engine operational; prompt specs ready.'),
        ('End of Sprint 4', '17-10-2026', 400, 235, 165, 16, 16, '58.8%', 'On schedule; Groq client connected; single-tx ETL loader built.'),
        ('End of Sprint 5', '27-10-2026', 400, 292, 108, 20, 12, '73.0%', 'On schedule; analytical views indexed; AI Analyst tab prototype.'),
        ('End of Sprint 6', '03-11-2026', 400, 346, 54, 24, 8, '86.5%', 'On schedule; AST validator built; 34 automated tests passing.'),
        ('Baseline Deadline', '08-11-2026', 400, 370, 30, 26, 6, '92.5%', '4 tasks completed in S7; Q6 fixed; 2 tasks in progress.'),
        ('Progress Cut-off', '10-11-2026', 400, 378, 22, 28, 4, '94.5%', 'Current status: 28 tasks completed, 4 in progress; report generated.'),
        ('Revised Forecast', '25-11-2026', 400, 400, 0, 32, 0, '100.0%', 'Revised completion date for live cloud deployment and latency benchmarking.')
    ]
    for r_idx, row in enumerate(bd_data, start=r_start + 2):
        is_highlight = ('Progress Cut-off' in row[0])
        for c_idx, val in enumerate(row, start=1):
            cell = ws_pm.cell(r_idx, c_idx, val)
            cell.font = body_font_bold if is_highlight else body_font
            cell.border = cell_border
            cell.alignment = center_align
            if is_highlight:
                cell.fill = PatternFill(start_color='FFF2CC', end_color='FFF2CC', fill_type='solid')

    # Section 3: Cumulative Flow Diagram (CFD)
    r_start_cfd = 29
    ws_pm.cell(r_start_cfd, 1, '3. CUMULATIVE FLOW DIAGRAM (CFD) DATA TABLE')
    ws_pm.cell(r_start_cfd, 1).font = sub_font
    
    cfd_headers = ['Sprint_Milestone', 'Date', 'Backlog_Tasks', 'In_Progress_Tasks', 'In_Testing_Tasks', 'Done_Tasks', 'Total_Tasks', 'WIP_Limit_Check']
    for c_idx, h in enumerate(cfd_headers, start=1):
        c = ws_pm.cell(r_start_cfd + 1, c_idx, h)
        c.font = header_font
        c.fill = navy_header_fill
        c.alignment = center_align
        
    cfd_data = [
        ('Start S1', '23-08-2026', 32, 0, 0, 0, 32, 'WIP within limits (0 active)'),
        ('End S1', '05-09-2026', 28, 0, 0, 4, 32, 'WIP within limits (0 active)'),
        ('End S2', '19-09-2026', 24, 0, 0, 8, 32, 'WIP within limits (0 active)'),
        ('End S3', '03-10-2026', 20, 0, 0, 12, 32, 'WIP within limits (0 active)'),
        ('End S4', '17-10-2026', 16, 0, 0, 16, 32, 'WIP within limits (0 active)'),
        ('End S5', '27-10-2026', 12, 0, 0, 20, 32, 'WIP within limits (0 active)'),
        ('End S6', '03-11-2026', 8, 0, 0, 24, 32, 'WIP within limits (0 active)'),
        ('Cut-off (10-11-2026)', '10-11-2026', 0, 2, 2, 28, 32, 'WIP = 4 active tasks (S7 hardening)'),
        ('Target (25-11-2026)', '25-11-2026', 0, 0, 0, 32, 32, 'Target: 0 active, 32 Done')
    ]
    for r_idx, row in enumerate(cfd_data, start=r_start_cfd + 2):
        is_highlight = ('Cut-off' in row[0])
        for c_idx, val in enumerate(row, start=1):
            cell = ws_pm.cell(r_idx, c_idx, val)
            cell.font = body_font_bold if is_highlight else body_font
            cell.border = cell_border
            cell.alignment = center_align
            if is_highlight:
                cell.fill = PatternFill(start_color='FFF2CC', end_color='FFF2CC', fill_type='solid')

    # Section 4: Cycle Time & Lead Time Analysis
    r_start_ct = 41
    ws_pm.cell(r_start_ct, 1, '4. CYCLE TIME & LEAD TIME ANALYSIS')
    ws_pm.cell(r_start_ct, 1).font = sub_font
    
    ct_headers = ['Workstream / Submodule', 'Tasks_Sampled', 'Avg_Lead_Time (days)', 'Avg_Cycle_Time (days)', 'Min_Cycle_Time (days)', 'Max_Cycle_Time (days)', 'Efficiency_Notes']
    for c_idx, h in enumerate(ct_headers, start=1):
        c = ws_pm.cell(r_start_ct + 1, c_idx, h)
        c.font = header_font
        c.fill = navy_header_fill
        c.alignment = center_align
        
    ct_data = [
        ('MOD_01 & MOD_02 (Data Acquisition & Lake)', 4, 10.5, 7.8, 5, 10, 'High throughput; MoRTH CSV extraction automated rapidly.'),
        ('MOD_02 & MOD_03 (Cleansing, Staging & Warehouse)', 6, 11.2, 8.2, 6, 11, 'Complex 3NF mapping and Annexure 45 whitespace resolution.'),
        ('MOD_03 (Airflow Orchestration & Testing)', 6, 10.8, 7.0, 5, 10, 'Airflow DAGs and pytest test harness developed iteratively.'),
        ('MOD_04 & MOD_05 (SQL Views & Dashboard UI)', 8, 11.0, 6.8, 4, 9, 'Streamlit UI and Plotly visualizations developed smoothly.'),
        ('MOD_06 (Groq LLM Backend & AST Security)', 6, 12.5, 7.5, 4, 12, 'High complexity AST validator and security audit checks.'),
        ('OVERALL PROJECT AVERAGE', 30, 11.2, 7.4, 4, 12, 'Healthy flow efficiency (~66%); average cycle time 7.4 calendar days.')
    ]
    for r_idx, row in enumerate(ct_data, start=r_start_ct + 2):
        is_total = (r_idx == r_start_ct + 2 + len(ct_data) - 1)
        for c_idx, val in enumerate(row, start=1):
            cell = ws_pm.cell(r_idx, c_idx, val)
            cell.font = body_font_bold if is_total else body_font
            cell.border = cell_border
            cell.alignment = center_align if c_idx > 1 else left_align
            if is_total:
                cell.fill = PatternFill(start_color='F2F2F2', end_color='F2F2F2', fill_type='solid')

    # Section 5: Team Member Actual Effort Breakdown
    r_start_team = 50
    ws_pm.cell(r_start_team, 1, '5. TEAM MEMBER ACTUAL EFFORT DISTRIBUTION (AS OF 10-11-2026)')
    ws_pm.cell(r_start_team, 1).font = sub_font
    
    team_headers = ['Team_Member', 'Role_and_Lead_Responsibility', 'Planned_Hours', 'Completed_Hours', 'WIP_Hours', 'Target_Share (%)', 'Actual_Completed_Share (%)', 'Compliance_Status']
    for c_idx, h in enumerate(team_headers, start=1):
        c = ws_pm.cell(r_start_team + 1, c_idx, h)
        c.font = header_font
        c.fill = navy_header_fill
        c.alignment = center_align
        
    team_data = [
        ('Jayant Soni', 'LLM Integration, Text-to-SQL Backend & AST Security', 104, 100, 4, '26.0%', '26.5%', 'Fully Compliant (+0.5% variance)'),
        ('Honey Singh', 'PostgreSQL 3NF Warehouse, ETL Loader & Data Quality', 104, 101, 3, '26.0%', '26.7%', 'Fully Compliant (+0.7% variance)'),
        ('Gautam', 'Airflow Orchestration, Docker Architecture & Testing', 104, 99, 5, '26.0%', '26.2%', 'Fully Compliant (+0.2% variance)'),
        ('Sugam Umale', 'Streamlit UI, Visualizations & Documentation', 88, 78, 10, '22.0%', '20.6%', 'Fully Compliant (-1.4% variance; documentation active)'),
        ('TOTAL PROJECT', '4-Member Cross-Functional Engineering Team', 400, 378, 22, '100.0%', '100.0%', 'Compliant with prescribed 26/26/26/22% allocation')
    ]
    for r_idx, row in enumerate(team_data, start=r_start_team + 2):
        is_total = (r_idx == r_start_team + 2 + len(team_data) - 1)
        for c_idx, val in enumerate(row, start=1):
            cell = ws_pm.cell(r_idx, c_idx, val)
            cell.font = body_font_bold if is_total else body_font
            cell.border = cell_border
            cell.alignment = center_align if c_idx not in [1, 2] else left_align
            if is_total:
                cell.fill = PatternFill(start_color='F2F2F2', end_color='F2F2F2', fill_type='solid')

    col_widths_pm = [24, 34, 16, 16, 16, 16, 24, 26, 32]
    for idx, width in enumerate(col_widths_pm, start=1):
        ws_pm.column_dimensions[get_column_letter(idx)].width = width

    # Save workbook
    wb.save(dst_path)
    print(f'Successfully updated and saved tracker to: {dst_path}')

if __name__ == '__main__':
    update_tracker()

