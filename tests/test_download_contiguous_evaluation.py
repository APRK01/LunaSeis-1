import unittest

from scripts.download_contiguous_evaluation import reconcile_plan


class ContiguousEvaluationDownloadTests(unittest.TestCase):
    def test_reconciles_exact_plan(self):
        plan={"status":"planned_not_downloaded","product_count":1,"total_bytes":3,"products":[{"path":"x","bytes":3}]}
        self.assertEqual(reconcile_plan(plan),plan["products"])

    def test_rejects_duplicate(self):
        plan={"status":"planned_not_downloaded","product_count":2,"total_bytes":6,"products":[{"path":"x","bytes":3},{"path":"x","bytes":3}]}
        with self.assertRaises(ValueError):reconcile_plan(plan)
