# ROAD INSIGHT — Database Design

This directory (`db_design/`) contains the complete data engineering artifacts for the Road Insight project.
The database has been designed as a highly normalized (3NF), production-ready PostgreSQL schema suited for analytics and Text-to-SQL/LLM applications.

## Directory Structure

*   **`DATA_AUDIT.md`**: Comprehensive file-by-file dataset audit.
*   **`DATA_DICTIONARY.md`**: Column-level dictionary mapped to the normalized schema.
*   **`DATA_CLEANING_LOG.md`**: Record of all data transformations and cleaning rules.
*   **`NORMALIZATION_REPORT.md`**: Detailed 1NF, 2NF, 3NF analysis and dependency tracking.
*   **`BUSINESS_GLOSSARY.md`**: Definitions of business terms based strictly on the source data.
*   **`schema_metadata.json`**: Semantic metadata for Text-to-SQL model integration.
*   **`ERD.md`**: Mermaid-based Entity-Relationship Diagram of the schema.
*   **`sql/`**: PostgreSQL execution scripts.
    *   `01_create_schema.sql`: Initializes `road_insight` schema.
    *   `02_create_tables.sql`: Core normalized tables and staging tables.
    *   `03_create_constraints.sql`: PKs, FKs, CHECK constraints.
    *   `04_create_indexes.sql`: Performance indexes for analytical queries.
    *   `05_insert_reference_data.sql`: Seed data for dimensions and data sources.
    *   `06_load_data.sql`: Core loading SQL reference transformations (used alongside Python ETL).
    *   `07_validation_queries.sql`: Post-load quality and sanity checks.
    *   `08_views.sql`: Denormalized analytical views for dashboard/LLM use.
    *   `09_audit_tables.sql`: Audit log tables (`etl_run_log`, `etl_run_table_log`, `rejected_rows`, `dq_check_results`).
*   **`06_etl_loader.py`**: Hardened Python script that reads raw CSVs, performs wide-to-long unpivoting, cleans Indian numerals, enforces atomic transactions, tracks rejections, and logs run metrics into PostgreSQL.

## Architecture: Staging (`stg_*`) vs Direct Ingestion

- **`stg_*` Tables (`02_create_tables.sql`)**: Staging tables were initially designed for intermediate staging of unparsed raw CSV extracts.
- **Production Pipeline**: The hardened `06_etl_loader.py` script bypasses transient database staging by performing transformations in-memory with Pandas, enforcing single-transaction atomicity directly into the normalized core fact tables (`national_historical_stats`, `state_annual_stats`, etc.), with full audit tracking in `road_insight.etl_run_log` and `road_insight.rejected_rows`. The `stg_*` DDL is retained for backward compatibility and manual SQL-only ETL staging pipelines.

## Instructions to Deploy

1.  Review `DATA_AUDIT.md` to understand the raw data landscape.
2.  Run `sql/01_create_schema.sql` through `sql/05_insert_reference_data.sql` and `sql/09_audit_tables.sql` in sequence on PostgreSQL.
3.  Install Python dependencies: `pip install pandas psycopg2-binary sqlalchemy`
4.  Run the ETL loader:
    *   **Live Mode**: `python 06_etl_loader.py --conn "postgresql://user:pass@localhost:5432/roadinsight"`
    *   **Dry-Run Mode (offline verification)**: `python 06_etl_loader.py --dry-run`
    *   **Verbose Logging**: `python 06_etl_loader.py --conn "..." --verbose --log-dir logs/`
5.  Run `sql/07_validation_queries.sql` or `python scripts/run_checks.py` to verify referential integrity and data completeness.
6.  Run `sql/08_views.sql` to instantiate the reporting views.
