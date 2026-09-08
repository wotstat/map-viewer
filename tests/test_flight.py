import os
import sys
import unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'res', 'scripts', 'client', 'gui', 'mods'))
from wotstat_local_maps.flight import flightOffset


class FlightTest(unittest.TestCase):
    def test_forward_respects_yaw_and_pitch(self):
        import math
        x, y, z = flightOffset(math.pi / 2, math.pi / 6, 1, 0, 0, 60)
        self.assertAlmostEqual(x, 60 * math.cos(math.pi / 6))
        self.assertAlmostEqual(y, -30)
        self.assertAlmostEqual(z, 0)

    def test_vertical_is_world_vertical(self):
        self.assertEqual(flightOffset(1, 1, 0, 0, 1, 60), (0, 60, 0))

    def test_diagonal_does_not_exceed_speed(self):
        import math
        delta = flightOffset(0.7, 0.5, 1, 1, 1, 60)
        self.assertAlmostEqual(math.sqrt(sum(x*x for x in delta)), 60)

    def test_idle_does_not_drift(self):
        self.assertEqual(flightOffset(1, 1, 0, 0, 0, 60), (0, 0, 0))


if __name__ == '__main__':
    unittest.main()
