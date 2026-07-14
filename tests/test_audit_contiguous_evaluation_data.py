import unittest

from scripts.audit_contiguous_evaluation_data import full_day_status, merged_duration_seconds


class ContiguousEvaluationDataAuditTests(unittest.TestCase):
    def test_status_boundaries(self):
        self.assertEqual(full_day_status(.1,.1),"usable_integrity")
        self.assertEqual(full_day_status(.11,.1),"questionable_integrity")
        self.assertEqual(full_day_status(.21,.1),"reject_integrity")

    def test_merged_scannable_duration(self):
        self.assertEqual(merged_duration_seconds([0,60,120]),720)
        self.assertEqual(merged_duration_seconds([0,1200]),1200)
