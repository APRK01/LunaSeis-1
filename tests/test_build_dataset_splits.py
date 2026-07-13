import unittest
from datetime import datetime, timedelta

from scripts.build_dataset_splits import assign_groups


class DatasetSplitTests(unittest.TestCase):
    def test_test_groups_are_never_train_or_validation(self):
        times = {f"g{i}": datetime(1970, 1, 1) + timedelta(days=i) for i in range(10)}
        result = assign_groups(times, {"g2", "g7"})
        self.assertEqual(result["g2"], "test")
        self.assertEqual(result["g7"], "test")
        self.assertEqual(sum(v == "validation" for v in result.values()), 2)
