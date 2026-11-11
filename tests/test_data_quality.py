"""
Unit and Integration Tests for Data Quality & Reconciliation Framework
File: tests/test_data_quality.py
"""

import sys
import unittest
from pathlib import Path
import pandas as pd

# Add repo root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

import importlib.util
dq_path = BASE_DIR / 'scripts' / 'run_checks.py'
spec = importlib.util.spec_from_file_location('run_checks', str(dq_path))
dq = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dq)

etl_path = BASE_DIR / 'db_design' / '06_etl_loader.py'
spec_etl = importlib.util.spec_from_file_location('etl_loader', str(etl_path))
etl = importlib.util.module_from_spec(spec_etl)
spec_etl.loader.exec_module(etl)


class TestDataQualityFramework(unittest.TestCase):
    """Test suite for R1-R6 and Q1-Q8 checks."""

    @classmethod
    def setUpClass(cls):
        # Load in-memory datasets via ETL loader
        cls.tracker = etl.ETLTracker()
        cls.data_dict = {}
        for name, fn in etl.LOADERS:
            cls.data_dict[name] = fn(None, cls.tracker)
        cls.framework = dq.DQFramework(conn=None, data_dict=cls.data_dict)
        cls.results = cls.framework.run_all()
        cls.results_by_id = {r['check_id']: r for r in cls.results}

    def test_all_14_checks_executed(self):
        expected_ids = ['R1', 'R2', 'R3', 'R4', 'R5', 'R6',
                        'Q1', 'Q2', 'Q3', 'Q4', 'Q5', 'Q6', 'Q7', 'Q8']
        for cid in expected_ids:
            self.assertIn(cid, self.results_by_id, f"Check {cid} was not executed!")

    def test_r1_reconciliation(self):
        r1 = self.results_by_id['R1']
        self.assertEqual(r1['status'], 'PASS')
        self.assertEqual(r1['rows_failed'], 0)

    def test_r3_r4_totals(self):
        r3 = self.results_by_id['R3']
        r4 = self.results_by_id['R4']
        self.assertEqual(r3['status'], 'PASS')
        self.assertEqual(r4['status'], 'PASS')

    def test_q1_referential_integrity(self):
        q1 = self.results_by_id['Q1']
        self.assertEqual(q1['status'], 'PASS')
        self.assertEqual(q1['rows_failed'], 0)

    def test_q2_duplicate_uniqueness(self):
        q2 = self.results_by_id['Q2']
        self.assertEqual(q2['status'], 'PASS')
        self.assertEqual(q2['rows_failed'], 0)

    def test_q4_mandatory_non_null(self):
        q4 = self.results_by_id['Q4']
        self.assertEqual(q4['status'], 'PASS')
        self.assertEqual(q4['rows_failed'], 0)

    def test_q6_upstream_discrepancy_documented(self):
        q6 = self.results_by_id['Q6']
        self.assertEqual(q6['status'], 'WARN')
        self.assertEqual(q6['rows_failed'], 161)
        self.assertIn('MoRTH source discrepancy', q6['detail'])


if __name__ == '__main__':
    unittest.main()

