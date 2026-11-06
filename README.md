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

Streamlit Community Cloud cannot connect to PostgreSQL running on your local
computer. Use a hosted PostgreSQL database, then add these secrets in
**Manage app -> Settings -> Secrets**:

```toml
READONLY_DATABASE_URL = "postgresql+psycopg://readonly_user:YOUR_PASSWORD@YOUR_HOST:5432/roadinsight"
GROQ_API_KEY = "your_groq_api_key"
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
