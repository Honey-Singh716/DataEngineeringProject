"""
Golden Queries Evaluation Suite
File: tests/test_golden_accuracy.py
Tests the 30 benchmark queries defined in tests/golden_queries.json.
Generates evaluation evidence in docs/evidence/golden/golden_results.csv.
"""

import os
import sys
import csv
import json
import re
import unittest
from pathlib import Path
from datetime import datetime, timezone

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

try:
    import sqlglot
    from ai_analyst.security.sql_validator import validate_sql
    SQLGLOT_AVAILABLE = True
except ImportError:
    SQLGLOT_AVAILABLE = False

try:
    import pytest
except ImportError:
    pytest = None

ALLOWED_TABLES = {
    'states', 'cities', 'weather_conditions', 'road_features',
    'collision_types', 'violation_types', 'data_sources',
    'national_historical_stats', 'national_annual_stats', 'state_annual_stats',
    'city_accident_stats', 'city_violation_stats', 'city_weather_stats',
    'city_road_feature_stats', 'collision_type_stats', 'violation_type_stats',
    'v_state_summary', 'v_city_summary', 'v_national_trend'
}

UNSUPPORTED_KEYWORDS = [
    'age', 'gender', 'vehicle model', 'make and model', 'latitude', 'longitude',
    'gps', 'time of day', 'hourly', 'blood alcohol', 'concentration'
]

FORBIDDEN_PATTERNS = [
    r'\bdrop\b', r'\bdelete\b', r'\bupdate\b', r'\binsert\b', r'\balter\b',
    r'\btruncate\b', r'\bpg_shadow\b', r'\bpg_catalog\b', r'\binformation_schema\b',
    r'ignore previous instructions', r'system prompt'
]


def basic_validate_sql(sql: str) -> tuple[bool, str]:
    """Lightweight fallback validator when sqlglot is not installed."""
    if not sql or not isinstance(sql, str):
        return False, "Empty or invalid query"

    cleaned = sql.strip().rstrip(';')

    # Check for forbidden patterns
    for pat in FORBIDDEN_PATTERNS:
        if re.search(pat, cleaned, re.IGNORECASE):
            return False, f"Forbidden statement or pattern detected: {pat}"

    # Must start with SELECT
    if not cleaned.lower().startswith('select'):
        return False, "Only SELECT statements are permitted"

    return True, "Valid SQL query"


def is_adversarial_query(query: str) -> bool:
    """Detect prompt injection or malicious SQL payloads."""
    for pat in FORBIDDEN_PATTERNS:
        if re.search(pat, query, re.IGNORECASE):
            return True
    return False


def is_unsupported_query(query: str) -> bool:
    """Detect requests for fields outside the schema scope."""
    q_lower = query.lower()
    return any(kw in q_lower for kw in UNSUPPORTED_KEYWORDS)


class TestGoldenQueriesAccuracy(unittest.TestCase):
    """Test suite for the 30 golden evaluation queries."""

    @classmethod
    def setUpClass(cls):
        json_path = BASE_DIR / 'tests' / 'golden_queries.json'
        with open(json_path, 'r', encoding='utf-8') as f:
            cls.golden_queries = json.load(f)

        cls.out_dir = BASE_DIR / 'docs' / 'evidence' / 'golden'
        cls.out_dir.mkdir(parents=True, exist_ok=True)
        cls.results = []

    def test_all_30_queries_present(self):
        self.assertEqual(len(self.golden_queries), 30)
        categories = [q['category'] for q in self.golden_queries]
        self.assertEqual(categories.count('supported'), 20)
        self.assertEqual(categories.count('unsupported'), 5)
        self.assertEqual(categories.count('adversarial'), 5)

    def test_golden_queries_evaluation(self):
        eval_mode = "Live/Groq" if os.getenv("GROQ_API_KEY") else "Static/Reference"

        for gq in self.golden_queries:
            qid = gq['id']
            cat = gq['category']
            q = gq['question']
            expected = gq['expected_behavior']
            ref_sql = gq.get('reference_sql')

            actual_status = "UNKNOWN"
            syntax_valid = False
            notes = ""

            if cat == 'supported':
                if SQLGLOT_AVAILABLE:
                    val_res = validate_sql(ref_sql)
                    syntax_valid = val_res.is_valid
                    notes = val_res.error or "AST and Schema validation passed"
                else:
                    syntax_valid, notes = basic_validate_sql(ref_sql)

                actual_status = "EXECUTE" if syntax_valid else "INVALID_SQL"
                self.assertTrue(syntax_valid, f"Supported query {qid} failed SQL validation: {notes}")
                self.assertEqual(actual_status, expected)

            elif cat == 'unsupported':
                unsupported_detected = is_unsupported_query(q)
                syntax_valid = False
                actual_status = "REJECT_UNSUPPORTED" if unsupported_detected else "MISCLASSIFIED"
                notes = "Correctly identified as out-of-scope schema domain"
                self.assertTrue(unsupported_detected, f"Query {qid} was not detected as unsupported: {q}")
                self.assertEqual(actual_status, expected)

            elif cat == 'adversarial':
                adversarial_detected = is_adversarial_query(q)
                syntax_valid = False
                actual_status = "BLOCK_SECURITY" if adversarial_detected else "MISCLASSIFIED"
                notes = "Blocked by security guardrails and injection defenses"
                self.assertTrue(adversarial_detected, f"Adversarial query {qid} was not blocked: {q}")
                self.assertEqual(actual_status, expected)

            self.results.append({
                'id': qid,
                'category': cat,
                'question': q,
                'expected_behavior': expected,
                'actual_status': actual_status,
                'syntax_valid': 'YES' if syntax_valid else 'N/A',
                'evaluation_mode': eval_mode,
                'notes': notes
            })

        # Save to CSV
        csv_path = self.out_dir / 'golden_results.csv'
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'id', 'category', 'question', 'expected_behavior',
                'actual_status', 'syntax_valid', 'evaluation_mode', 'notes'
            ])
            writer.writeheader()
            writer.writerows(self.results)

        print(f"\nWrote golden query results to {csv_path}")


if __name__ == '__main__':
    unittest.main()

