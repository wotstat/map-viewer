import os
import sys
import unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'res', 'scripts', 'client', 'gui', 'mods'))
from wotstat_local_maps.flight import flightOffset


class FlightTest(unittest.TestCase):
    def test_forward_keeps_height_at_any_pitch(self):
        import math
        x, y, z = flightOffset(math.pi / 2, math.pi / 6, 1, 0, 0, 60)
        self.assertAlmostEqual(x, 60)
        self.assertAlmostEqual(y, 0)
        self.assertAlmostEqual(z, 0)
        for pitch in (-math.pi / 2, math.pi / 2):
            self.assertEqual(flightOffset(0, pitch, 1, 0, 0, 60), (0, 0, 60))

    def test_acceleration_and_braking(self):
        from wotstat_local_maps.flight import advanceVelocity
        velocity = advanceVelocity((0, 0, 0), (0, 0, 1), 20, 0.05)
        self.assertEqual(velocity, (0, 0, 5))
        velocity = advanceVelocity(velocity, (0, 0, 1), 20, 0.05)
        self.assertEqual(velocity, (0, 0, 10))
        braking = advanceVelocity(velocity, (0, 0, 0), 20, 0.05)
        self.assertTrue(0 < braking[2] < velocity[2])
        for _ in range(30):
            braking = advanceVelocity(braking, (0, 0, 0), 20, 0.05)
        self.assertEqual(braking, (0, 0, 0))

    def test_velocity_limit_and_frame_independent_braking(self):
        from wotstat_local_maps.flight import advanceVelocity
        velocity = advanceVelocity((0, 0, 19), (0, 0, 1), 20, 0.1)
        self.assertEqual(velocity, (0, 0, 20))
        full = advanceVelocity(velocity, (0, 0, 0), 20, 0.1)
        half = advanceVelocity(velocity, (0, 0, 0), 20, 0.05)
        half = advanceVelocity(half, (0, 0, 0), 20, 0.05)
        self.assertAlmostEqual(full[2], half[2])

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
