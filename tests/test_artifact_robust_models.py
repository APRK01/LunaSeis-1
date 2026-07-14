import unittest

import numpy as np

from scripts.train_artifact_robust_models import robust_transform


class ArtifactRobustModelTests(unittest.TestCase):
    def test_level_transform_is_bounded_and_preserves_gap_mask(self):
        values=np.array([10.,11.,-1.,10000.,12.])
        result=robust_transform(values,"robust_level",length=8)
        self.assertEqual(result.shape,(2,8))
        self.assertEqual(result[1,2],0)
        self.assertLessEqual(float(np.max(np.abs(result[0]))),20)

    def test_difference_requires_two_valid_adjacent_samples(self):
        values=np.array([10.,11.,-1.,13.,15.])
        result=robust_transform(values,"robust_difference",length=6)
        self.assertEqual(result[1,:4].tolist(),[1.,0.,0.,1.])

    def test_rejects_excessive_gaps(self):
        self.assertIsNone(robust_transform(np.array([-1.,-1.,3.,4.]),"robust_level"))


if __name__=="__main__":unittest.main()
