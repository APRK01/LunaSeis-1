import unittest

from scripts.audit_all_nonshallow import classify


class AllBatchAuditTests(unittest.TestCase):
    def test_primary_boundary_policy(self):
        t = (0.2, 0.5, 1.0, 10.0)
        self.assertEqual(classify(0.2, 1.0, *t), "usable_integrity")
        self.assertEqual(classify(0.21, 1.0, *t), "questionable_integrity")
        self.assertEqual(classify(0.1, 10.01, *t), "reject_integrity")


if __name__ == "__main__":
    unittest.main()
