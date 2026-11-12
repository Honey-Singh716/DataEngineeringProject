# Text-to-SQL Pipeline Latency Breakdown Report

- **Execution Timestamp:** 2026-11-11 19:28:31 UTC
- **Sample Size:** 5 representative queries × 5 iterations = 25 measured runs
- **Environment:** macOS Python 3.13 (`.venv`)
- **Live Groq API Status:** NOT RUN (Sandbox Offline / No GROQ_API_KEY)
- **Mean Local Non-LLM Overhead:** `16.573 ms`
- **Median Local Non-LLM Overhead:** `9.837 ms`
- **P95 Local Non-LLM Overhead:** `35.61 ms`

## Detailed Stage Latency Breakdown

| Pipeline Stage | Subsystem / Operation | Mean Latency (ms) | Operational Status |
|---|---|---|---|
| **Stage 1** | Input Validation (`text_to_sql_service.py`) | `0.0003` | VERIFIED (Actual) |
| **Stage 2** | Schema Context Synthesis (`schema_builder.py`) | `0.0001` | VERIFIED (Actual) |
| **Stage 3** | Prompt Construction (`prompt_templates.py`) | `0.0006` | VERIFIED (Actual) |
| **Stage 4** | Groq Cloud LLM Inference (`groq_client.py`) | `NOT RUN` | NOT RUN |
| **Stage 5** | JSON Response Deserialization (`sql_generator.py`) | `0.0072` | VERIFIED (Actual) |
| **Stage 6** | AST SQL Validation (`sqlglot` dialect) | `0.6435` | VERIFIED (Actual) |
| **Stage 7** | Relational In-Memory Execution | `0.237` | VERIFIED (Actual) |
| **Stage 8** | Result Processing & DataFrame Packaging | `0.019` | VERIFIED (Actual) |
| **Stage 9** | Plotly Chart Generation & Serialization | `15.6656` | VERIFIED (Actual) |
| **Total Non-LLM** | **Complete Local Pipeline** | **`16.573 ms`** | **VERIFIED (Actual)** |

### LLM Dominance Assessment
- **Status:** **UNMEASURED AS EMPIRICAL FACT** (Network isolation prevented live calls).
- **Architectural Analysis:** In live cloud deployments, network roundtrips to `api.groq.com` range between **400 ms and 750 ms**. With local processing overhead measured at **16.573 ms**, cloud inference would mathematically represent ~99% of total interactive latency; however, per project integrity rules, this percentage is classified as an **architectural projection**, NOT an empirical measurement.
