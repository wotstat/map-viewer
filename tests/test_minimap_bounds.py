# coding: utf-8
import os
import sys
import unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'res', 'scripts', 'client', 'gui', 'mods'))
from wotstat_map_viewer.minimap_bounds import getMinimapBounds


class MinimapBoundsTest(unittest.TestCase):
    def test_oder_uses_full_texture_bounds(self):
        self.assertEqual(getMinimapBounds(((-200, -535), (300, 515))),
                         ((-535, -535), (515, 515)))

    def test_horizontal_story_map_uses_full_texture_bounds(self):
        self.assertEqual(getMinimapBounds(((-550, -250), (550, 250))),
                         ((-550, -550), (550, 550)))

    def test_square_map_keeps_its_offset(self):
        bounds = ((-450, -510), (550, 490))
        self.assertEqual(getMinimapBounds(bounds), bounds)


if __name__ == '__main__':
    unittest.main()
