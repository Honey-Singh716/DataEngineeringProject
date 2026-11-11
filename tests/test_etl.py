"""
Unit and Integration Tests for Hardened ETL Loader
File: tests/test_etl.py
"""

import sys
import unittest
from unittest.mock import MagicMock, patch
from pathlib import Path
import pandas as pd

# Add repo root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

import importlib.util
etl_path = BASE_DIR / 'db_design' / '06_etl_loader.py'
spec = importlib.util.spec_from_file_location('etl_loader', str(etl_path))
etl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(etl)


class TestETLNumberParsing(unittest.TestCase):
    """Tests for Indian number parsing, null coercion, and non-integer rejection."""

    def setUp(self):
        self.tracker = etl.ETLTracker()

    def test_valid_indian_numbers(self):
        self.assertEqual(etl.parse_indian_number('4,56,959', self.tracker), 456959)
        self.assertEqual(etl.parse_indian_number('1,72,890', self.tracker), 172890)
        self.assertEqual(etl.parse_indian_number(12345, self.tracker), 12345)
        self.assertEqual(etl.parse_indian_number('12.0', self.tracker), 12)
        self.assertEqual(self.tracker.rows_rejected, 0)

    def test_null_coercion(self):
        for val in ['NA', 'N/A', '#N/A', 'Na', '', '-', '--', None, float('nan')]:
            res = etl.parse_indian_number(val, self.tracker)
            self.assertIsNone(res, f"Failed for val: {val}")
        self.assertEqual(self.tracker.rows_rejected, 0)
        self.assertGreater(self.tracker.null_coerced, 0)

    def test_non_integer_rejection(self):
        """Non-integer numbers like '12.7' must be rejected to rejected_rows."""
        res = etl.parse_indian_number('12.7', self.tracker, source_file='test.csv',
                                      row_num=10, raw_row={'val': '12.7'}, field_name='test_field')
        self.assertIsNone(res)
        self.assertEqual(self.tracker.rows_rejected, 1)
        self.assertEqual(len(self.tracker.rejected_rows), 1)
        rej = self.tracker.rejected_rows[0]
        self.assertEqual(rej['source_file'], 'test.csv')
        self.assertEqual(rej['row_number'], 10)
        self.assertIn('non_integer_value', rej['reason'])


class TestETLNormalization(unittest.TestCase):
    """Tests for canonical city and state normalization."""

    def test_city_normalization(self):
        self.assertEqual(etl.normalize_city_name('allahabad (prayagraj)'), 'Allahabad (Prayagraj)')
        self.assertEqual(etl.normalize_city_name('khozikode'), 'Kozhikode')
        self.assertEqual(etl.normalize_city_name('vadodra'), 'Vadodara')
        self.assertEqual(etl.normalize_city_name('vijaywada city'), 'Vijayawada')
        self.assertEqual(etl.normalize_city_name('Delhi'), 'Delhi')

    def test_state_normalization(self):
        self.assertEqual(etl.normalize_state_name('j & k #'), 'Jammu & Kashmir')
        self.assertEqual(etl.normalize_state_name('j & k'), 'Jammu & Kashmir')
        self.assertEqual(etl.normalize_state_name('dadra & nagar haveli*'), 'Dadra & Nagar Haveli and Daman & Diu')
        self.assertEqual(etl.normalize_state_name('Punjab'), 'Punjab')


class TestETLDryRun(unittest.TestCase):
    """Integration test: Dry-run across all 9 loaders with real CSV sources."""

    def test_dry_run_full_pipeline(self):
        summary = etl.run_etl(dry_run=True)
        self.assertEqual(summary['status'], 'SUCCESS')
        self.assertTrue(summary['dry_run'])
        self.assertEqual(summary['rows_loaded'], 1299)
        self.assertEqual(summary['rows_read'], 351)

        # Verify all 9 tables match expected counts
        table_counts = {t['table_name']: t['rows_loaded'] for t in summary['tables']}
        for table_name, expected in etl.EXPECTED_COUNTS.items():
            self.assertIn(table_name, table_counts)
            self.assertEqual(table_counts[table_name], expected,
                             f"Count mismatch in {table_name}: got {table_counts[table_name]}, expected {expected}")


class TestETLAtomicRollback(unittest.TestCase):
    """Test error handling and atomicity during failure."""

    def test_atomic_rollback_on_loader_error(self):
        mock_engine = MagicMock()
        mock_conn = MagicMock()
        mock_engine.begin.return_value.__enter__.return_value = mock_conn

        # Simulate exception on second loader
        failing_loaders = [
            ('table1', lambda conn, tracker: tracker.increment_loaded(10)),
            ('table2', MagicMock(side_effect=RuntimeError("Simulated database write error"))),
        ]

        with patch.object(etl, 'create_engine', return_value=mock_engine):
            with patch.object(etl, 'LOADERS', failing_loaders):
                with self.assertRaises(RuntimeError):
                    etl.run_etl(conn_str="postgresql://user:pass@localhost:5432/db", dry_run=False)


if __name__ == '__main__':
    unittest.main()
