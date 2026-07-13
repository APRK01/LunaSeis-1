import unittest
from datetime import datetime,timedelta
import numpy as np

from scripts.audit_independent_background import gap_fraction,overlaps


class IndependentBackgroundAuditTests(unittest.TestCase):
    def test_gap_and_event_buffer(self):
        self.assertEqual(gap_fraction(np.array([-1,0,1,-1])),0.5)
        event=datetime(1971,1,1,12)
        self.assertTrue(overlaps(event,event+timedelta(minutes=10),[event],timedelta(hours=1)))
        self.assertFalse(overlaps(event+timedelta(hours=2),event+timedelta(hours=3),[event],timedelta(hours=1)))
