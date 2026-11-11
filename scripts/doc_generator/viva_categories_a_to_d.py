"""
doc_generator/viva_categories_a_to_d.py
Viva questions and answers for Categories A through D.
"""

CATEGORY_A = {
    "category": "A. Project Overview",
    "questions": [
        {
            "q": "Why did you build this project?",
            "short": "To bridge fragmented Indian road accident statistics into a unified, mathematically reconciled, and high-performance relational warehouse with conversational AI querying.",
            "tech": "Official MoRTH and OGD datasets are distributed across disparate CSV files and PDFs with varying granularities, unstandardized padding, and conflicting reporting baselines. RoadInsight India normalizes these datasets into a 3NF PostgreSQL schema, validates integrity through automated checks, and democratizes access via Streamlit and Text-to-SQL.",
            "ref": "docs/final_audit/FINAL_INDEPENDENT_AUDIT_REPORT.md Section 2; db_design/sql/01_create_schema.sql",
            "tradeoff": "The system relies on annual government aggregate publications; real-time telemetry or micro-level incident FIRs are not publicly available."
        },
        {
            "q": "What problem does it solve?",
            "short": "It eliminates data silos, resolves cross-dataset reporting discrepancies, enforces referential constraints, and allows non-technical stakeholders to query safety statistics naturally.",
            "tech": "Analysts previously had to manually reconcile heterogeneous spreadsheets with formatting anomalies (like comma-separated numbers and trailing header spaces). RoadInsight automates ingestion, guarantees atomic rollback on failure, indexes queries for 1.3ms execution, and secures LLM-driven analytics.",
            "ref": "db_design/06_etl_loader.py; scripts/run_checks.py (Rules R1–R6)",
            "tradeoff": "Historical multi-decade datasets (1970–2023) lack state-level breakdowns, limiting long-term longitudinal analysis to national totals."
        },
        {
            "q": "What is its main contribution?",
            "short": "A production-grade, mathematically reconciled data pipeline coupled with a zero-trust AST-validated Text-to-SQL architecture that prevents SQL injection.",
            "tech": "The platform provides empirical proof resolving the 69-discrepancy (proving it resulted from comparing 2016 national totals to 2023 state sums) and solves the Annexure 45 padding bug. It also enforces least-privilege database role separation and AST-level query validation using sqlglot.",
            "ref": "docs/final_audit/DATA_RECONCILIATION_AUDIT.md; ai_analyst/security/sql_validator.py",
            "tradeoff": "The LLM pipeline relies on Groq cloud API availability; offline deployments require local model hosting."
        },
        {
            "q": "What makes it different from a normal dashboard?",
            "short": "It is an end-to-end data engineering platform with atomic ETL, strict database constraints, audit tables, and secure natural-language text-to-SQL querying rather than just a visual skin.",
            "tech": "Traditional dashboards connect directly to uncleaned CSV files or flat tables without referential integrity. RoadInsight India implements an atomic ETL loader, an audit lineage trail (etl_run_log, rejected_rows), database views, B-tree query optimization, and an AST security validator.",
            "ref": "dashboard/app.py; ai_analyst/services/text_to_sql_service.py",
            "tradeoff": "Added architectural complexity requires configuring PostgreSQL instances, connection pools, and environment secrets."
        }
    ]
}

CATEGORY_B = {
    "category": "B. Data Engineering",
    "questions": [
        {
            "q": "What is ETL?",
            "short": "ETL stands for Extract, Transform, Load—the automated pipeline that extracts raw data from CSVs, cleans and structures it in memory, and loads it into a database.",
            "tech": "Extract reads heterogeneous MoRTH CSVs. Transform trims column whitespace, strips commas from Indian numeric strings, casts values to nullable integers, and validates check constraints. Load streams staged data into PostgreSQL tables inside an atomic transaction.",
            "ref": "db_design/06_etl_loader.py",
            "tradeoff": "Batch ETL processing introduces latency between data publication and database availability compared to real-time stream processing."
        },
        {
            "q": "Why use Pandas?",
            "short": "Pandas provides vectorized in-memory data manipulation, robust NaN handling, and high-performance tabular transformations.",
            "tech": "Pandas enables rapid column-wise string stripping, conditional filtering, type conversion, and integration with SQLAlchemy's to_sql chunked loader. It allows pre-ingestion validation before database transaction initiation.",
            "ref": "db_design/06_etl_loader.py: Stages 2 & 3",
            "tradeoff": "Pandas loads entire datasets into RAM; for datasets exceeding hundreds of gigabytes, distributed frameworks like PySpark would be required."
        },
        {
            "q": "How do you handle missing data?",
            "short": "We distinguish between true zeros (recorded zero events) and missing values (unreported data), storing missing values as SQL NULL.",
            "tech": "Empty strings and 'NA' tokens are cast to pandas.NA and mapped to SQL NULL. In contrast, '0' is preserved as numeric zero. This preserves statistical integrity, preventing averages and rates from being falsely skewed.",
            "ref": "db_design/06_etl_loader.py; docs/METRIC_DICTIONARY.md",
            "tradeoff": "SQL queries computing ratios must explicitly use NULLIF() or COALESCE() to prevent division-by-zero errors."
        },
        {
            "q": "What is idempotency?",
            "short": "An idempotent pipeline produces the exact same system state regardless of how many times it is executed with the same input.",
            "tech": "The loader uses ON CONFLICT DO NOTHING for master dimension tables and manages transactional table truncations or upserts, ensuring re-running the ETL script does not generate duplicate records or inflate counts.",
            "ref": "db_design/sql/05_insert_reference_data.sql; db_design/06_etl_loader.py",
            "tradeoff": "Implementing idempotent upserts requires maintaining primary keys or unique index constraints on all target tables."
        },
        {
            "q": "What is atomicity?",
            "short": "Atomicity ensures that a group of database operations either all succeed together or all fail together with zero partial state committed.",
            "tech": "The ETL loader wraps table insertions inside SQLAlchemy's 'with engine.begin() as conn:' context manager. If an error occurs halfway through inserting 10,000 rows, the engine issues an automatic ROLLBACK.",
            "ref": "db_design/06_etl_loader.py: load_table_atomic()",
            "tradeoff": "Long-running atomic transactions hold database table locks, temporarily blocking concurrent writers."
        },
        {
            "q": "What happens if the sixth ETL loader fails?",
            "short": "The transaction for the sixth loader rolls back completely, leaving previously committed tables intact and logging the failure to etl_run_log.",
            "tech": "Because each table load operates in a discrete transactional unit, any unhandled exception triggers an immediate ROLLBACK for that table. The run status is recorded as 'FAILED' in etl_run_log with the error stack trace.",
            "ref": "db_design/06_etl_loader.py; db_design/sql/09_audit_tables.sql",
            "tradeoff": "The warehouse contains partially updated cross-table data until the failing loader is debugged and re-executed."
        },
        {
            "q": "How are rejected records stored?",
            "short": "Rejected records are captured in road_insight.rejected_rows with the run ID, target table, raw JSON payload, and rejection reason.",
            "tech": "When a row violates a check constraint, type cast, or schema rule, it is serialized to JSON and inserted into rejected_rows. Valid rows proceed to load, ensuring zero loss of analytical observability.",
            "ref": "db_design/sql/09_audit_tables.sql: rejected_rows table",
            "tradeoff": "Storing malformed payloads in JSONB consumes additional disk space in the audit schema."
        }
    ]
}

CATEGORY_C = {
    "category": "C. Database and PostgreSQL",
    "questions": [
        {
            "q": "Why PostgreSQL?",
            "short": "PostgreSQL 17 offers enterprise-grade ACID compliance, advanced SQL window functions, robust role-based security, and high-performance B-tree indexing.",
            "tech": "PostgreSQL provides strict schema enforcement via CHECK constraints, comprehensive EXPLAIN ANALYZE diagnostic tooling, role privilege isolation, and seamless integration with Python via SQLAlchemy and psycopg3.",
            "ref": "db_design/sql/01_create_schema.sql; db_design/README_DATABASE.md",
            "tradeoff": "Requires dedicated server management, memory tuning (shared_buffers, work_mem), and active connection pool configuration."
        },
        {
            "q": "What are primary and foreign keys?",
            "short": "A primary key uniquely identifies each record in a table; a foreign key links a record in one table to the primary key of another table to maintain referential integrity.",
            "tech": "In schema 'road_insight', states.state_id is a primary key, while state_annual_stats.state_id is a foreign key referencing states(state_id). PostgreSQL rejects any insert into state_annual_stats that references a non-existent state.",
            "ref": "db_design/sql/02_create_tables.sql; db_design/sql/03_create_constraints.sql",
            "tradeoff": "Foreign key enforcement adds a minor CPU overhead during high-volume batch inserts."
        },
        {
            "q": "Why use constraints?",
            "short": "Constraints guarantee data correctness at the database level, preventing corrupted or impossible data (like negative fatalities) from entering the warehouse.",
            "tech": "We enforce CHECK (total_accidents >= 0), CHECK (killed >= 0), and UNIQUE (state_id, year). Even if application validation fails, the database rejects invalid data.",
            "ref": "db_design/sql/03_create_constraints.sql",
            "tradeoff": "Violating a constraint raises an exception that must be trapped and handled cleanly by the application layer."
        },
        {
            "q": "What is indexing?",
            "short": "Indexing creates auxiliary data structures (like B-trees) that allow the database engine to locate matching rows in logarithmic time rather than scanning every row.",
            "tech": "Without an index, filtering 200,000 records requires reading all table blocks from disk (sequential scan). A B-tree index traverses hierarchical tree nodes, reducing page reads from 14,820 to 4.",
            "ref": "db_design/sql/04_create_indexes.sql; scripts/benchmarks/bench_index.py",
            "tradeoff": "Indexes consume additional RAM and disk space, and slow down INSERT/UPDATE operations as index nodes must be rebalanced."
        },
        {
            "q": "What is a composite index?",
            "short": "An index created on two or more columns of a table to accelerate queries that filter or sort by those columns together.",
            "tech": "We created idx_state_annual_state_year ON state_annual_stats (state_id, year). This allows the planner to satisfy WHERE state_id = 12 AND year = 2023 with a single index range scan.",
            "ref": "db_design/sql/04_create_indexes.sql",
            "tradeoff": "The index is only effective if queries filter by the leading column (state_id); filtering by year alone cannot fully leverage the composite index."
        },
        {
            "q": "Why can a sequential scan sometimes be faster?",
            "short": "For small tables or queries that retrieve a large percentage of table rows, sequential scans avoid index traversal overhead and read contiguous disk blocks sequentially.",
            "tech": "If a table has fewer than a few hundred rows (like our dimension tables), the entire table fits in a single memory page. The planner chooses a sequential scan because traversing an index tree would require extra page lookups.",
            "ref": "PostgreSQL Query Planner documentation; scripts/benchmarks/bench_index.py",
            "tradeoff": "As table row counts grow into hundreds of thousands, sequential scans rapidly become severe system bottlenecks."
        },
        {
            "q": "What is EXPLAIN ANALYZE?",
            "short": "A PostgreSQL command that actually executes a query and returns the real execution plan with true elapsed times and buffer hit statistics.",
            "tech": "Unlike plain EXPLAIN (which shows optimizer cost estimates), EXPLAIN (ANALYZE, BUFFERS) executes the query, showing the actual scan method (Index Scan vs Seq Scan), startup time, total time, and shared buffer hits.",
            "ref": "docs/evidence/benchmarks/EXPLAIN_ANALYZE_EVIDENCE.txt",
            "tradeoff": "Because EXPLAIN ANALYZE actually runs the query, executing it on heavy DML statements will modify data unless wrapped in a transaction rollback."
        },
        {
            "q": "What is connection pooling?",
            "short": "A technique that maintains a cache of open database connections for reuse, eliminating the overhead of opening and closing connections on every query.",
            "tech": "Creating a new PostgreSQL connection requires TCP handshakes, authentication, and process spawning (~30-50ms). SQLAlchemy's QueuePool maintains a pool of 10 connections, allowing queries to borrow an open connection in <0.5ms.",
            "ref": "dashboard/app.py: get_engine(); ai_analyst/database/connection.py",
            "tradeoff": "Idle connections consume memory on the PostgreSQL server (approximately 2–10 MB per connection process)."
        }
    ]
}

CATEGORY_D = {
    "category": "D. Text-to-SQL and LLM",
    "questions": [
        {
            "q": "What is Text-to-SQL?",
            "short": "The automated translation of natural language questions into syntactically valid and semantically correct SQL queries.",
            "tech": "Text-to-SQL bridges the gap between natural language prompts and structured relational databases, allowing users to query data without writing SQL code.",
            "ref": "ai_analyst/services/text_to_sql_service.py",
            "tradeoff": "Subject to LLM hallucinations, prompt injection risks, and semantic ambiguity if schema context is insufficient."
        },
        {
            "q": "How does the LLM generate SQL?",
            "short": "By conditioning on a curated system prompt containing table schemas, sample values, and domain instructions, the LLM predicts the target SQL tokens.",
            "tech": "The system prompt provides DDL definitions of allowed views and tables in schema 'road_insight'. The LLM generates standard PostgreSQL queries matching the user's intent.",
            "ref": "ai_analyst/llm/sql_generator.py; ai_analyst/llm/schema_builder.py",
            "tradeoff": "Providing extensive schema definitions increases prompt token consumption and slightly increases inference latency."
        },
        {
            "q": "What schema information is provided?",
            "short": "Only curated analytical tables and views in schema 'road_insight' with their column names and primary keys; staging and audit tables are excluded.",
            "tech": "We inject CREATE TABLE summaries for fact and dimension tables and view definitions. Staging tables (stg_*) and internal audit tables are omitted to minimize token overhead and prevent accidental staging queries.",
            "ref": "ai_analyst/security/table_allowlist.py: ALLOWED_TABLES",
            "tradeoff": "The LLM cannot answer queries regarding pipeline ingestion status or rejected row metadata."
        },
        {
            "q": "Why use Groq?",
            "short": "Groq provides ultra-fast LLM inference using custom LPU (Language Processing Unit) hardware, delivering inference speeds over 300 tokens/second.",
            "tech": "Standard cloud LLM endpoints take 2,000–4,000 ms to generate a response. Groq generates complete SQL queries in 400–600 ms, making conversational analytics viable for interactive dashboards.",
            "ref": "ai_analyst/llm/sql_generator.py; scripts/benchmarks/bench_latency.py",
            "tradeoff": "Cloud dependency requires external network access and adherence to Groq API rate limits."
        },
        {
            "q": "How do you validate generated SQL?",
            "short": "We parse the SQL string into an Abstract Syntax Tree (AST) using sqlglot, ensuring it is a single SELECT query referencing only allowlisted tables.",
            "tech": "The validator inspects the AST hierarchy. It blocks non-SELECT nodes, disallows dangerous functions (pg_sleep, pg_read_file), verifies table names against ALLOWED_TABLES, and automatically injects LIMIT 100.",
            "ref": "ai_analyst/security/sql_validator.py",
            "tradeoff": "Complex nested subqueries or vendor-specific SQL extensions may occasionally be rejected if sqlglot dialect rules are overly strict."
        },
        {
            "q": "What if the LLM generates incorrect SQL?",
            "short": "The query fails either at the AST validation stage or during database execution, triggering a clean fallback message without exposing internal database errors.",
            "tech": "If syntax is invalid, sqlglot raises a parse error. If validation passes but PostgreSQL returns an execution error, the exception is caught, logged securely, and masked before returning to the user.",
            "ref": "ai_analyst/services/text_to_sql_service.py: TextToSQLResponse",
            "tradeoff": "The user receives an error notification and must rephrase their question."
        },
        {
            "q": "What if SQL executes but returns an incorrect answer?",
            "short": "This is a semantic error; we mitigate this using detailed prompt instructions, column definitions, and evaluation against 30 golden queries.",
            "tech": "Semantic errors occur when SQL is valid but logic is flawed (e.g., using SUM instead of AVG). Golden queries benchmark semantic correctness across standard domain tasks.",
            "ref": "tests/golden_queries.json; tests/test_golden_accuracy.py",
            "tradeoff": "Without human verification or formal semantic checks, subtle query logic errors cannot always be caught automatically."
        },
        {
            "q": "How do you handle unsupported questions?",
            "short": "The system prompt instructs the LLM to identify out-of-scope questions and return a structured clarification or unsupported status flag.",
            "tech": "If a user asks about topics outside road safety (e.g., stock market or weather forecasts for tomorrow), the pipeline returns status='unsupported' and guides the user to domain topics.",
            "ref": "ai_analyst/llm/sql_generator.py: system prompt instructions",
            "tradeoff": "Borderline questions that combine domain topics with unavailable attributes may be partially misunderstood."
        },
        {
            "q": "Why is LLM inference slow?",
            "short": "LLMs generate output autoregressively, predicting one token at a time through billions of neural network parameters, compounded by internet roundtrip latency.",
            "tech": "Our benchmark shows cloud LLM inference takes 485 ms (median), while local PostgreSQL query execution takes 3.2 ms. The neural network computation and TLS network handshake dominate the latency budget.",
            "ref": "scripts/benchmarks/bench_latency.py; Chapter 11 Latency Profile",
            "tradeoff": "Interactive latency is fundamentally constrained by the speed of the LLM provider."
        },
        {
            "q": "What causes non-determinism?",
            "short": "Random sampling across token probability distributions causes variations in generated text; we set temperature=0.0 to maximize reproducibility.",
            "tech": "Even at temperature=0.0, floating-point non-associativity across parallel GPU/LPU execution threads can occasionally produce slight token differences across runs.",
            "ref": "ai_analyst/config.py: LLM_TEMPERATURE = 0.0",
            "tradeoff": "Low temperature eliminates creative rephrasing, but predictability is essential for SQL generation."
        }
    ]
}

