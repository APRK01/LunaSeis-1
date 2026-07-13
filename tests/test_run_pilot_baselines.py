import unittest
import numpy as np

from scripts.run_pilot_baselines import best_threshold, metrics


class PilotBaselineTests(unittest.TestCase):
    def test_threshold_and_metrics(self):
        scores=np.array([0.1,0.2,0.8,0.9]); labels=np.array([0,0,1,1])
        threshold=best_threshold(scores,labels)
        result=metrics(scores,labels,threshold)
        self.assertEqual(result["f1"],1.0)
