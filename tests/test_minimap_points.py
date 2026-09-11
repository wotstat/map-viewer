import os
import sys
import unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'res', 'scripts', 'client', 'gui', 'mods'))
from wotstat_local_maps.minimap_points import iterTeamPoints


class MinimapPointsTest(unittest.TestCase):
    def test_single_bases_ignore_arena_ids(self):
        points = list(iterTeamPoints(({7: (10, 20)}, {9: (30, 40)}), (), ()))
        self.assertEqual(points, [('AllyTeamBaseEntry', (10, 20), 0),
                                  ('EnemyTeamBaseEntry', (30, 40), 0)])

    def test_encounter_has_spawns_and_unnumbered_control_point(self):
        points = list(iterTeamPoints((), (((1, 2),), ((3, 4),)), ((5, 6),)))
        self.assertEqual(points, [('AllyTeamSpawnEntry', (1, 2), 1),
                                  ('EnemyTeamSpawnEntry', (3, 4), 1),
                                  ('ControlPointEntry', (5, 6), 0)])

    def test_multiple_bases_and_control_points_use_native_numbers(self):
        points = list(iterTeamPoints(({8: (1, 2), 20: (3, 4)},), (), ((5, 6), (7, 8))))
        self.assertEqual([p[2] for p in points], [1, 2, 2, 3])

    def test_empty_arena(self):
        self.assertEqual(list(iterTeamPoints(None, None, None)), [])
