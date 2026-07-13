import unittest
from datetime import datetime, timedelta

from scripts.build_background_manifest import overlaps_event


class BackgroundManifestTests(unittest.TestCase):
    def test_event_buffer_excludes_overlap(self):
        event = datetime(1971, 1, 1, 12)
        self.assertTrue(overlaps_event(event - timedelta(minutes=30), event + timedelta(minutes=30), [event], timedelta(hours=1)))
        self.assertFalse(overlaps_event(event + timedelta(hours=2), event + timedelta(hours=3), [event], timedelta(hours=1)))
