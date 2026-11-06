"""
scripts/test_ai_analyst.py
Interactive CLI testing interface for the Road Insight AI Analyst.

Usage:
    python scripts/test_ai_analyst.py
"""
import sys
import os
import time

# Ensure project root is in Python module search path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ai_analyst.config import settings
from ai_analyst.services.text_to_sql_service import run_text_to_sql
from ai_analyst.database.connection import check_readonly_connection


def print_banner():
    print("=" * 70)
    print("🚦 ROAD INSIGHT — AI ANALYST CLI TEST HARNESS")
    print("=" * 70)
    print(f"• LLM Model       : {settings.groq_model}")
    print(f"• Groq API Key    : {'Configured ✅' if settings.groq_configured else 'NOT CONFIGURED ❌'}")
    
    db_status = check_readonly_connection()
    if db_status['ok']:
        print(f"• Read-Only DB    : Connected ✅ (DB: {db_status['db_name']}, User: {db_status['db_user']})")
    else:
        print(f"• Read-Only DB    : PENDING SETUP ⚠️ ({db_status['message']})")
        print("  (Queries will be generated and validated, but DB execution requires setup_readonly_role.sql)")
    print("=" * 70)
    print("Type your questions below in plain English. Type 'exit' or 'q' to quit.\n")


def display_result(result):
    print("\n" + "-" * 70)
    print("[1] USER QUESTION:")
    print(f"    {result.question}")

    print("\n[2] GENERATED SQL:")
    if result.sql:
        indented_sql = "\n".join("    " + line for line in result.sql.splitlines())
        print(indented_sql)
    else:
        print("    [No SQL Generated - Question unsupported or clarification required]")

    print("\n[3] SQL VALIDATION STATUS:")
    if result.status == "validation_error":
        print(f"    FAILED ❌ : {result.error}")
    elif result.sql:
        print("    PASSED ✅ : All security layers validated (Single SELECT, schema check, allowlist, LIMIT)")
        if result.validation_warnings:
            for w in result.validation_warnings:
                print(f"    ⚠️ Warning: {w}")
    else:
        print("    SKIPPED (No SQL produced)")

    print("\n[4] QUERY EXECUTION STATUS:")
    if result.status == "success":
        print(f"    SUCCESS ✅ : {result.row_count} rows retrieved in {result.execution_time_ms:.1f} ms")
    elif result.status == "empty_result":
        print("    EMPTY RESULT ⚠️ : Query executed successfully but returned 0 rows.")
    elif result.status == "db_not_configured":
        print("    PENDING CONFIGURATION ⚠️ : Read-only DB account not yet configured in .env.")
    elif result.status == "execution_error":
        print(f"    EXECUTION ERROR ❌ : {result.error}")
    elif result.status in ("unsupported", "clarification_required"):
        print(f"    N/A : Question marked as '{result.status}' by AI engine.")
    else:
        print(f"    {result.status.upper()}: {result.error}")

    print("\n[5] RETURNED DATA:")
    if result.data is not None and not result.data.empty:
        # Display nicely formatted dataframe
        print(result.data.to_string(index=False))
    elif result.data is not None and result.data.empty:
        print("    (0 rows returned)")
    else:
        print("    (No data to display)")

    print("\n[6] AI EXPLANATION:")
    print(f"    {result.explanation or result.error or 'N/A'}")
    if result.chart_type:
        print(f"    [Suggested UI Visualization: {result.chart_type.upper()}] (Confidence: {result.confidence.upper()})")

    print("\n[7] TOTAL LATENCY:")
    print(f"    End-to-end time: {result.total_time_ms:.1f} ms (DB Time: {result.execution_time_ms:.1f} ms)")
    print("-" * 70 + "\n")


def main():
    print_banner()

    while True:
        try:
            user_input = input("Enter your question > ").strip()
            if not user_input:
                continue
            if user_input.lower() in ("exit", "quit", "q"):
                print("\nExiting Road Insight AI Analyst CLI. Goodbye! 🚦")
                break

            response = run_text_to_sql(user_input)
            display_result(response)

        except (KeyboardInterrupt, EOFError):
            print("\nExiting Road Insight AI Analyst CLI. Goodbye! 🚦")
            break
        except Exception as e:
            print(f"\n[ERROR] An unexpected error occurred: {e}\n")


if __name__ == "__main__":
    main()

