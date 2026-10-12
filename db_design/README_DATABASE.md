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
    *   `06_load_data.sql`: Core loading transformations (used with Python ETL script).
    *   `07_validation_queries.sql`: Post-load quality and sanity checks.
    *   `08_views.sql`: Denormalized analytical views for dashboard/LLM use.
*   **`06_etl_loader.py`**: Python script that reads the raw CSVs, performs the required wide-to-long (unpivoting) and cleaning transformations, and loads the data into PostgreSQL.

## Instructions to Deploy

1.  Review `DATA_AUDIT.md` to understand the raw data landscape.
2.  Run `sql/01_create_schema.sql` through `sql/05_insert_reference_data.sql` in sequence on your PostgreSQL instance.
3.  Install Python dependencies: `pip install pandas psycopg2-binary sqlalchemy`
4.  Run the ETL loader: `python 06_etl_loader.py --conn "postgresql://user:pass@localhost:5432/db_name"`
5.  Run `sql/06_load_data.sql` to execute in-database aggregations (if not handled by Python).
6.  Run `sql/07_validation_queries.sql` to verify referential integrity and data completeness.
7.  Run `sql/08_views.sql` to instantiate the reporting views.
