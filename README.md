# RoadInsight India 🇮🇳

An end-to-end Data Engineering project analyzing road accidents in India from 1970 to 2020. This project demonstrates the complete data lifecycle: extraction, transformation, loading, and visualization.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- PostgreSQL 12+
- Required Python packages: `pandas`, `sqlalchemy`, `psycopg2-binary`, `plotly`, `dash`, `streamlit`

### Installation
```bash
pip install pandas sqlalchemy psycopg2-binary plotly dash streamlit
```

### Setup PostgreSQL
Create the schema and load reference data:
```bash
psql -U postgres -f db_design/sql/01_create_schema.sql
psql -U postgres -f db_design/sql/02_create_tables.sql
psql -U postgres -f db_design/sql/03_create_constraints.sql
psql -U postgres -f db_design/sql/04_create_indexes.sql
psql -U postgres -f db_design/sql/05_insert_reference_data.sql
```

## 💻 Local Setup (Windows)

### Option A: Docker Path (Recommended for clean environment)
1. Ensure Docker Desktop is running on Windows.
2. Start the PostgreSQL 17 container:
   ```powershell
   docker compose up -d
   ```
3. Initialize the schema, ETL, views, and roles automatically using PowerShell:
   ```powershell
   .\scripts\setup_local.ps1 -Host "localhost" -Port 5432 -Database "roadinsight" -User "postgres"
   ```

### Option B: Non-Docker Path (Local PostgreSQL 17 Install)
1. Ensure PostgreSQL 17 service is active locally (port 5432).
2. Execute the setup script or run the sequential SQL migrations and ETL loader:
   ```powershell
   # Automated setup via PowerShell:
   .\scripts\setup_local.ps1

   # Or manual step-by-step:
   psql -U postgres -f db_design/sql/01_create_schema.sql
   psql -U postgres -d roadinsight -f db_design/sql/02_create_tables.sql
   psql -U postgres -d roadinsight -f db_design/sql/03_create_constraints.sql
   psql -U postgres -d roadinsight -f db_design/sql/04_create_indexes.sql
   psql -U postgres -d roadinsight -f db_design/sql/05_insert_reference_data.sql
   python db_design/06_etl_loader.py --conn "postgresql://postgres:<password>@localhost:5432/roadinsight"
   psql -U postgres -d roadinsight -f db_design/sql/08_views.sql
   ```


### Load Data
Run the ETL loader to populate the database:
```bash
python db_design/06_etl_loader.py --conn "postgresql://user:password@localhost:5432/roadinsight"
```

### Run the Dashboard
```bash
streamlit run dashboard/app.py
```
Access the dashboard at http://localhost:8501

### Deploy to Streamlit Community Cloud

Streamlit Community Cloud runs in a remote container and cannot connect to `localhost`.
Use a hosted PostgreSQL database (e.g., Neon, Supabase, Render), then configure secrets in
**Manage app -> Settings -> Secrets** in TOML format:

```toml
# Dashboard connection (with access to analytical views)
DASHBOARD_DATABASE_URL = "postgresql+psycopg://roadinsight_dashboard:YOUR_PASSWORD@YOUR_HOST:5432/roadinsight?sslmode=require"

# AI Analyst connection (isolated read-only execution)
READONLY_DATABASE_URL = "postgresql+psycopg://roadinsight_readonly:YOUR_PASSWORD@YOUR_HOST:5432/roadinsight?sslmode=require"

# Groq LLM API
GROQ_API_KEY = "your_groq_api_key"
GROQ_MODEL = "openai/gpt-oss-120b"
QUERY_TIMEOUT_SECONDS = 3
MAX_RESULT_ROWS = 100
```

The app uses the `psycopg` driver, which is compatible with the Python runtime
used by Streamlit Community Cloud. Redeploy after committing `requirements.txt`.

## 📂 Project Structure

```
roadinsight-india/
├── data/                      # Raw CSV datasets
├── DataSets/                  # Cleaned datasets
├── db_design/                 # PostgreSQL schema and ETL scripts
│   ├── sql/                   # SQL migration scripts
│   ├── 06_etl_loader.py       # ETL pipeline
│   ├── BUSINESS_GLOSSARY.md   # Business glossary
│   ├── DATA_DICTIONARY.md     # Data dictionary
│   └── ...                    # Documentation
├── dashboard/                 # Streamlit frontend
│   └── app.py                 # Main dashboard application
├── EDA.ipynb                  # Exploratory Data Analysis
└── README.md                  # Project documentation
```

## 📊 Features

### Data Pipeline
- **ETL Automation**: Extracts data from raw CSVs, cleans it, and loads it into a normalized PostgreSQL database
- **Data Transformation**: Unpivots wide-format tables, parses Indian number formats, and standardizes values
- **Referential Integrity**: Enforces foreign key constraints between tables
- **Validation**: Includes SQL queries to validate data quality and completeness

### Dashboard
- **Overview**: National statistics, trends, and comparison charts
- **Geographic Analysis**: State-wise and city-wise accident data with interactive maps
- **Temporal Analysis**: Yearly trends, monthly breakdowns, and time-series analysis
- **Accident Analysis**: Types of accidents, causes, and victim demographics
- **Vehicle Analysis**: Vehicle categories involved in accidents
- **Severity Analysis**: Killed vs injured ratios and risk factors

## 📚 Documentation

- **[BUSINESS_GLOSSARY.md](db_design/BUSINESS_GLOSSARY.md)**: Defines business terms and KPIs
- **[DATA_DICTIONARY.md](db_design/DATA_DICTIONARY.md)**: Complete schema documentation
- **[ERD.md](db_design/ERD.md)**: Entity-Relationship Diagram of the database
- **[DATA_AUDIT.md](db_design/DATA_AUDIT.md)**: Data quality assessment
- **[DATA_CLEANING_LOG.md](db_design/DATA_CLEANING_LOG.md)**: Detailed cleaning steps
- **[NORMALIZATION_REPORT.md](db_design/NORMALIZATION_REPORT.md)**: Database normalization details
- **[schema_metadata.json](db_design/schema_metadata.json)**: Automated metadata

## 🛠️ Tech Stack

- **Language**: Python 3.x
- **Database**: PostgreSQL 12+
- **Data Processing**: pandas, NumPy
- **ETL**: Custom Python scripts
- **Visualization**: Plotly, Dash
- **Frontend**: Streamlit

## 🤝 Contributing

Feel free to fork the repository, create a feature branch, and submit a pull request.

## 📝 License

This project is for educational purposes and demonstrates data engineering concepts.
