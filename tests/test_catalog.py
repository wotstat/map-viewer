# coding: utf-8
import os
import sys
import unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'res', 'scripts', 'client', 'gui', 'mods'))
from wotstat_local_maps.catalog import groupArenas

class CatalogTest(unittest.TestCase):
    def test_map_has_only_its_own_modes_and_stable_default(self):
        records = [dict(key=65538, geometry='02', name=u'B', mode='domination', modeLabel=u'Encounter'),
                   dict(key=2, geometry='02', name=u'B', mode='ctf', modeLabel=u'Standard'),
                   dict(key=1, geometry='01', name=u'A', mode='ctf', modeLabel=u'Standard')]
        rows = groupArenas(records)
        self.assertEqual([r['key'] for r in rows], [1, 2])
        self.assertEqual([m['key'] for m in rows[1]['modes']], [2, 65538])
        self.assertEqual([m['key'] for m in rows[0]['modes']], [1])
        self.assertEqual(records[0]['key'], 65538)

if __name__ == '__main__':
    unittest.main()
