import unittest
from datetime import datetime

from scripts.build_preprocessing_manifest import mapped_time


class PreprocessingManifestTests(unittest.TestCase):
    def test_nominal_mapping_keeps_fractional_seconds(self):
        self.assertEqual(mapped_time("1971-01-01T00:00:00", "1.25"), datetime(1971, 1, 1, 0, 0, 1, 250000))
