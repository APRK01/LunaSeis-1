import unittest
from datetime import datetime

from scripts.build_nonshallow_download_plan import product_names, required_dates


class NonshallowPlanTests(unittest.TestCase):
    def test_normal_window_needs_one_day(self):
        self.assertEqual(len(required_dates(datetime(1975, 1, 2, 12, 0))), 1)

    def test_midnight_boundaries_add_adjacent_days(self):
        before = required_dates(datetime(1975, 1, 2, 0, 1))
        after = required_dates(datetime(1975, 1, 2, 23, 58))
        self.assertEqual([value.date().isoformat() for value in before], ["1975-01-01", "1975-01-02"])
        self.assertEqual([value.date().isoformat() for value in after], ["1975-01-02", "1975-01-03"])

    def test_product_names_are_channel_specific(self):
        self.assertEqual(product_names("S14", 1972, 5, "MHZ"), ("xa.s14.00.mhz.1972.005.0.mseed", "xa.s14.00.mhz.1972.005.0.xml"))
        self.assertEqual(product_names("S14", 1972, 5, "ATT"), ("xa.s14..att.1972.005.0.mseed", "xa.s14..att.1972.005.0.xml"))


if __name__ == "__main__":
    unittest.main()
