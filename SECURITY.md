# Security Policy & Credential Management — Road Insight India

## 1. Overview & Architecture

Road Insight India follows defense-in-depth principles across all database interactions, ETL processes, and user-facing analytical features.

Key security controls include:
- **Least-Privilege Database Roles**: The application separates administrative schema migrations from analytical queries. Read-only users cannot perform DDL, DML, or access unapproved/staging tables.
- **SQLGlot AST Security Validation**: All LLM-generated SQL queries are parsed into Abstract Syntax Trees (AST) in PostgreSQL dialect and validated before execution (single SELECT only, table allowlist enforcement, no catalog access, automated `LIMIT 100` injection).
- **Session-Level Guardrails**: All read-only connections enforce `default_transaction_read_only = on` and a strict `statement_timeout = '3000ms'`.
- **Environment Isolation**: Credentials, database URLs, and API keys are loaded strictly via environment variables (`.env` file or Streamlit Cloud Secrets) and are git-ignored.

---

## 2. ⚠️ Credential Rotation & Git History Notice

> [!WARNING]
> **Historical Password Exposure & Rotation Notice**
> 
> Prior commits in the git history of this repository (such as early demonstration commits) contained hardcoded default credentials (specifically `ReadOnlyPass123!Safe`).
>
> In accordance with academic project guidelines, **git history has intentionally NOT been rewritten** to maintain commit reproducibility and grading integrity.
>
> **Action Required for Deployment / Production:**
> 1. Any live or production deployment of this database **MUST manually rotate the password** for `roadinsight_readonly` and `postgres`.
> 2. The old password must not be reused under any circumstances.
> 3. Use the updated setup script `scripts/setup_readonly_role.sql` which requires supplying a fresh password via `-v ro_password="<secure_password>"`.

---

## 3. How to Configure Credentials Safely

### Local Development
1. Copy the template:
   ```bash
   cp .env.example .env
   ```
2. Set unique, strong passwords in `.env`:
   ```ini
   GROQ_API_KEY=gsk_your_actual_key_here
   GROQ_MODEL=openai/gpt-oss-120b
   READONLY_DATABASE_URL=postgresql://roadinsight_readonly:YOUR_ROTATED_PASSWORD@localhost:5432/roadinsight
   ```
3. Run role setup with the rotated password:
   ```bash
   psql -U postgres -d roadinsight -v ro_password="YOUR_ROTATED_PASSWORD" -f scripts/setup_readonly_role.sql
   ```

### Streamlit Community Cloud
Add your configuration in **Manage app -> Settings -> Secrets** in TOML format:
```toml
GROQ_API_KEY = "gsk_..."
GROQ_MODEL = "openai/gpt-oss-120b"
READONLY_DATABASE_URL = "postgresql+psycopg://roadinsight_readonly:YOUR_ROTATED_PASSWORD@YOUR_HOST:5432/roadinsight"
QUERY_TIMEOUT_SECONDS = 3
MAX_RESULT_ROWS = 100
```

---

## 4. Automated Secret Scanning (`tests/test_no_secrets.py`)

A regression test is included in the test suite to continuously verify that no passwords, API keys (`gsk_`, `sk-`), or credentials are committed to git-tracked files:
```bash
pytest tests/test_no_secrets.py -v
```
