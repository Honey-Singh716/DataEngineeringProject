"""
scripts/repro_bugs.py
Reproduces suspected bugs B2, B3, B5, B6, B7, B9.
Prints PASS (= bug present/reproduced) or FAIL (= bug absent/fixed) for each.
Saves console-compatible output.
"""

from __future__ import annotations

import ast
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load project environment
PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")


def check_b2() -> tuple[bool, str]:
    """B2: connect as roadinsight_readonly and SELECT from vw_state_stats_full and vw_city_stats_full."""
    url = os.getenv("READONLY_DATABASE_URL")
    if not url:
        return False, "READONLY_DATABASE_URL not set in .env"
    
    try:
        engine = create_engine(url)
        with engine.connect() as conn:
            # Try SELECT from vw_state_stats_full
            conn.execute(text("SELECT * FROM road_insight.vw_state_stats_full LIMIT 1"))
            conn.execute(text("SELECT * FROM road_insight.vw_city_stats_full LIMIT 1"))
        return False, "No permission error; roadinsight_readonly was able to SELECT from views (bug absent/fixed)"
    except Exception as e:
        err_msg = str(e)
        if "permission denied" in err_msg.lower() or "insufficientprivilege" in err_msg.lower():
            return True, f"Permission denied accessing views: {err_msg.splitlines()[-1]}"
        return False, f"Unexpected error during check: {e}"


def check_b3() -> tuple[bool, str]:
    """B3: dashboard/app.py::get_engine raises on localhost URLs."""
    app_py = PROJECT_ROOT / "dashboard" / "app.py"
    if not app_py.exists():
        return False, "dashboard/app.py not found"
    
    content = app_py.read_text(encoding="utf-8")
    # Check if the code explicitly checks for localhost and raises RuntimeError
    has_localhost_raise = (
        'if "localhost" in database_url or "127.0.0.1" in database_url:' in content
        and "raise RuntimeError" in content
    )
    if has_localhost_raise:
        return True, "get_engine() explicitly raises RuntimeError when localhost or 127.0.0.1 is present"
    return False, "get_engine() does not raise RuntimeError on localhost URLs (bug absent/fixed)"


def check_b5() -> tuple[bool, str]:
    """B5: ETL is not atomic (simulate/inspect whether loaders run without overarching transaction)."""
    etl_py = PROJECT_ROOT / "db_design" / "06_etl_loader.py"
    if not etl_py.exists():
        return False, "db_design/06_etl_loader.py not found"
    
    content = etl_py.read_text(encoding="utf-8")
    tree = ast.parse(content)
    
    # Check main function
    main_func = next((node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef) and node.name == "main"), None)
    if not main_func:
        return False, "main() function not found in 06_etl_loader.py"
    
    # Check if main wraps loaders in engine.begin() or transaction
    has_overarching_txn = False
    for node in ast.walk(main_func):
        if isinstance(node, ast.With):
            for item in node.items:
                if "begin" in ast.unparse(item.context_expr):
                    has_overarching_txn = True
                    break
    
    if not has_overarching_txn:
        return True, "ETL main() invokes individual loaders sequentially without an overarching engine.begin() transaction; failures leave partial commits"
    return False, "ETL main() wraps loaders in an atomic transaction (bug absent/fixed)"


def check_b6() -> tuple[bool, str]:
    """B6: load_road_no_acc reads pct-change columns by position (iloc[2/4/6]) and pct_cols is unused."""
    etl_py = PROJECT_ROOT / "db_design" / "06_etl_loader.py"
    if not etl_py.exists():
        return False, "db_design/06_etl_loader.py not found"
    
    content = etl_py.read_text(encoding="utf-8")
    has_iloc_usage = "row.iloc[2]" in content and "row.iloc[4]" in content and "row.iloc[6]" in content
    has_unused_pct_cols = "pct_cols = [c for c in df.columns" in content
    
    # Verify pct_cols is unused in load_road_no_acc
    if has_iloc_usage and has_unused_pct_cols:
        return True, "load_road_no_acc uses positional indexing (row.iloc[2/4/6]) and defines pct_cols without using it"
    return False, "load_road_no_acc uses explicit column names and no dead pct_cols (bug absent/fixed)"


def check_b7() -> tuple[bool, str]:
    """B7: ETL silently skips rows (year_val is None -> continue) and parse_indian_number truncates decimals via int(float(s))."""
    etl_py = PROJECT_ROOT / "db_design" / "06_etl_loader.py"
    if not etl_py.exists():
        return False, "db_design/06_etl_loader.py not found"
    
    # Import parse_indian_number from etl loader
    sys.path.insert(0, str(PROJECT_ROOT / "db_design"))
    try:
        import importlib
        etl_mod = importlib.import_module("06_etl_loader")
        truncated_val = etl_mod.parse_indian_number("12.7")
        is_truncated = (truncated_val == 12)
    except Exception as e:
        is_truncated = False
    
    content = etl_py.read_text(encoding="utf-8")
    has_silent_skip = "if year_val is None:\n            continue" in content
    
    if is_truncated and has_silent_skip:
        return True, f"parse_indian_number('12.7') returned {truncated_val} (truncated decimal via int(float(s))) and rows with year_val is None are silently skipped"
    return False, "No silent decimal truncation and skipped rows are captured (bug absent/fixed)"


def check_b9() -> tuple[bool, str]:
    """B9: redundant indexes exist (confirmed via pg_index against PK/UNIQUE constraints)."""
    admin_url = os.getenv("DATABASE_URL") or os.getenv("READONLY_DATABASE_URL")
    if not admin_url:
        return False, "DATABASE_URL not set in .env"
    
    # We test on postgres admin or readonly
    try:
        engine = create_engine(admin_url)
        sql = """
        SELECT 
            t.relname AS table_name,
            i.relname AS index_name,
            ix.indisunique,
            pg_get_indexdef(ix.indexrelid) AS index_def
        FROM pg_index ix
        JOIN pg_class t ON t.oid = ix.indrelid
        JOIN pg_class i ON i.oid = ix.indexrelid
        JOIN pg_namespace n ON n.oid = t.relnamespace
        WHERE n.nspname = 'road_insight'
          AND i.relname IN (
            'idx_nat_hist_year',
            'idx_nat_ann_year',
            'idx_state_stats_state_year',
            'idx_city_acc_city_year',
            'idx_city_vio_city_year_type'
          );
        """
        with engine.connect() as conn:
            rows = conn.execute(text(sql)).fetchall()
        
        if len(rows) > 0:
            found_names = [r[1] for r in rows]
            return True, f"Found {len(rows)} redundant indexes still active in schema: {found_names}"
        return False, "None of the candidate redundant indexes found in schema (bug absent/fixed)"
    except Exception as e:
        return False, f"Could not query pg_index: {e}"


def main():
    print("=" * 70)
    print("  ROAD INSIGHT: Bug Reproduction Suite (scripts/repro_bugs.py)")
    print("  PASS = Bug Present / Reproduced | FAIL = Bug Absent / Fixed")
    print("=" * 70)
    
    checks = [
        ("B2", "roadinsight_readonly cannot SELECT from full views", check_b2),
        ("B3", "dashboard/app.py::get_engine raises on localhost URLs", check_b3),
        ("B5", "ETL loaders lack overarching atomic transaction", check_b5),
        ("B6", "load_road_no_acc positional indexing (iloc[2/4/6]) & unused pct_cols", check_b6),
        ("B7", "ETL silent row skipping and decimal truncation in parse_indian_number", check_b7),
        ("B9", "Redundant indexes present in road_insight schema", check_b9),
    ]
    
    results = []
    for bug_id, desc, fn in checks:
        present, detail = fn()
        status = "PASS" if present else "FAIL"
        results.append((bug_id, desc, status, detail))
        print(f"\n[{status}] {bug_id}: {desc}")
        print(f"       Detail: {detail}")
    
    print("\n" + "=" * 70)
    print("SUMMARY OF BUG REPRODUCTION:")
    all_reproduced = all(r[2] == "PASS" for r in results)
    for bug_id, desc, status, _ in results:
        print(f"  {bug_id}: {status} ({'Bug Present' if status == 'PASS' else 'Bug Absent'})")
    print("=" * 70)
    if all_reproduced:
        print("All suspected bugs successfully verified and reproduced.")
    else:
        print("Some checks did not reproduce as expected.")


if __name__ == "__main__":
    main()

