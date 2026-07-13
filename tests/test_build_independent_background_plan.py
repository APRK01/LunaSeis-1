import unittest

from scripts.build_independent_background_plan import ranked_days


class IndependentBackgroundPlanTests(unittest.TestCase):
    def test_ranking_is_deterministic_and_bounded(self):
        days=list(range(1,366))
        self.assertEqual(ranked_days("S12",1971,days,32),ranked_days("S12",1971,days,32))
        self.assertEqual(len(ranked_days("S12",1971,days,32)),32)
        self.assertNotEqual(ranked_days("S12",1971,days,32),ranked_days("S14",1971,days,32))
