"""
scripts/verify_readonly_security.py
Comprehensive database security verification for the roadinsight_readonly role.
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import create_engine, text
from ai_analyst.config import settings

def run_security_audit():
    print("=" * 70)
    print("🔒 ROAD INSIGHT — READ-ONLY ROLE SECURITY AUDIT")
    print("=" * 70)
    
    if not settings.db_configured:
        print("❌ Error: READONLY_DATABASE_URL is not configured.")
        return False
        
    engine = create_engine(
        settings.readonly_database_url,
        connect_args={"options": "-csearch_path=road_insight,public"}
    )
    
    passed_checks = 0
    total_checks = 0
    
    def check(name, test_func):
        nonlocal passed_checks, total_checks
        total_checks += 1
        try:
            success, msg = test_func()
            if success:
                print(f"  [PASS] {name}: {msg}")
                passed_checks += 1
                return True
            else:
                print(f"  [FAIL] {name}: {msg}")
                return False
        except Exception as e:
            print(f"  [ERROR] {name}: Unexpected exception - {e}")
            return False

    with engine.connect() as conn:
        # Check 1: Login & current_user
        def test_current_user():
            row = conn.execute(text("SELECT current_user, session_user, current_database();")).fetchone()
            if row[0] == "roadinsight_readonly":
                return True, f"Connected as '{row[0]}' to database '{row[2]}'"
            return False, f"Expected user 'roadinsight_readonly', got '{row[0]}'"
        check("1. Role Identity", test_current_user)

        # Check 2: Role attributes (no superuser, createdb, createrole)
        def test_role_attributes():
            row = conn.execute(text("""
                SELECT rolsuper, rolcreaterole, rolcreatedb, rolinherit 
                FROM pg_roles 
                WHERE rolname = 'roadinsight_readonly';
            """)).fetchone()
            if not row:
                return False, "Could not query pg_roles for roadinsight_readonly"
            rolsuper, rolcreaterole, rolcreatedb, rolinherit = row
            if not rolsuper and not rolcreaterole and not rolcreatedb:
                return True, f"rolsuper={rolsuper}, rolcreaterole={rolcreaterole}, rolcreatedb={rolcreatedb}"
            return False, f"Privilege violation: super={rolsuper}, createrole={rolcreaterole}, createdb={rolcreatedb}"
        check("2. No Elevated Privileges", test_role_attributes)

        # Check 3: Read-only transaction status
        def test_transaction_read_only():
            row = conn.execute(text("SHOW transaction_read_only;")).fetchone()
            if row[0].lower() in ("on", "true", "yes", "1"):
                return True, f"transaction_read_only is '{row[0]}'"
            return False, f"transaction_read_only is '{row[0]}' (expected 'on')"
        check("3. Read-Only Transaction Setting", test_transaction_read_only)

        # Check 4: Approved analytical table SELECT
        def test_approved_table_select():
            row = conn.execute(text("SELECT count(*) FROM road_insight.state_annual_stats;")).fetchone()
            return True, f"SELECT on state_annual_stats succeeded (count={row[0]})"
        check("4. Approved Table SELECT", test_approved_table_select)

        # Check 5: Staging table SELECT rejection
        def test_staging_select_rejected():
            try:
                conn.execute(text("SELECT * FROM road_insight.stg_large_cities;"))
                return False, "SELECT on staging table succeeded (SECURITY BREACH)"
            except Exception as e:
                conn.rollback()
                return True, f"SELECT on stg_large_cities properly denied: {str(e).splitlines()[0]}"
        check("5. Staging Table SELECT Denied", test_staging_select_rejected)

        # Check 6: INSERT rejection
        def test_insert_rejected():
            try:
                conn.execute(text("INSERT INTO road_insight.states (state_name, state_type) VALUES ('TestState', 'State');"))
                return False, "INSERT succeeded (SECURITY BREACH)"
            except Exception as e:
                conn.rollback()
                return True, f"INSERT properly denied: {str(e).splitlines()[0]}"
        check("6. INSERT Statement Denied", test_insert_rejected)

        # Check 7: UPDATE rejection
        def test_update_rejected():
            try:
                conn.execute(text("UPDATE road_insight.states SET is_active = false WHERE state_id = 1;"))
                return False, "UPDATE succeeded (SECURITY BREACH)"
            except Exception as e:
                conn.rollback()
                return True, f"UPDATE properly denied: {str(e).splitlines()[0]}"
        check("7. UPDATE Statement Denied", test_update_rejected)

        # Check 8: DELETE rejection
        def test_delete_rejected():
            try:
                conn.execute(text("DELETE FROM road_insight.states WHERE state_id = 999;"))
                return False, "DELETE succeeded (SECURITY BREACH)"
            except Exception as e:
                conn.rollback()
                return True, f"DELETE properly denied: {str(e).splitlines()[0]}"
        check("8. DELETE Statement Denied", test_delete_rejected)

        # Check 9: DROP table rejection
        def test_drop_rejected():
            try:
                conn.execute(text("DROP TABLE road_insight.cities CASCADE;"))
                return False, "DROP TABLE succeeded (CRITICAL BREACH)"
            except Exception as e:
                conn.rollback()
                return True, f"DROP TABLE properly denied: {str(e).splitlines()[0]}"
        check("9. DROP Statement Denied", test_drop_rejected)

        # Check 10: CREATE table rejection
        def test_create_rejected():
            try:
                conn.execute(text("CREATE TABLE road_insight.hack_table (id int);"))
                return False, "CREATE TABLE succeeded (SECURITY BREACH)"
            except Exception as e:
                conn.rollback()
                return True, f"CREATE TABLE properly denied: {str(e).splitlines()[0]}"
        check("10. CREATE Statement Denied", test_create_rejected)

        # Check 11: 7 Approved Views Verification
        approved_views = [
            "vw_state_yoy_comparison",
            "vw_national_trends",
            "vw_city_violation_summary",
            "vw_city_weather_summary",
            "vw_city_road_feature_summary",
            "vw_collision_type_summary",
            "vw_violation_type_summary",
        ]
        def test_approved_views():
            view_results = []
            all_ok = True
            for v in approved_views:
                try:
                    r = conn.execute(text(f"SELECT count(*) FROM road_insight.{v};")).fetchone()
                    view_results.append(f"{v}: {r[0]} rows")
                except Exception as e:
                    conn.rollback()
                    all_ok = False
                    view_results.append(f"{v}: FAILED ({e})")
            if all_ok:
                return True, f"All 7 approved views accessible: {', '.join(view_results)}"
            return False, f"View failure: {', '.join(view_results)}"
        check("11. Approved 7 Views Functional", test_approved_views)

        # Check 12: Restricted data_sources table access
        def test_data_sources_restriction():
            try:
                r = conn.execute(text("SELECT count(*) FROM road_insight.data_sources;")).fetchone()
                return True, f"data_sources table accessible ({r[0]} rows). Check if explicitly approved."
            except Exception as e:
                conn.rollback()
                return True, f"data_sources properly restricted: {str(e).splitlines()[0]}"
        check("12. data_sources Table Access Status", test_data_sources_restriction)

    print("=" * 70)
    print(f"AUDIT SUMMARY: {passed_checks}/{total_checks} checks passed.")
    print("=" * 70)
    return passed_checks == total_checks

if __name__ == "__main__":
    success = run_security_audit()
    sys.exit(0 if success else 1)

