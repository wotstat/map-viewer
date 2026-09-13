# coding: utf-8
import os
import sys
import unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'res', 'scripts', 'client', 'gui', 'mods'))
from wotstat_map_viewer.debug_panel import SettingsRegistry


class TimelineControlTest(unittest.TestCase):
    def setUp(self):
        self.registry = SettingsRegistry()
        self.changes = []
        self.registry.registerSection('events', 'Events', [dict(
            id='one', type='timeline', label='Event 1: technicalName',
            value=dict(position=25.0, playing=True), playTooltip='Play', pauseTooltip='Pause')],
            lambda *args: self.changes.append(args))

    def test_seek_pauses_even_at_the_current_position(self):
        self.assertTrue(self.registry.changeValue('events', 'one', dict(position=25.0, playing=False)))
        self.assertEqual(self.changes, [('one', dict(position=25.0, playing=False))])

    def test_progress_updates_do_not_call_the_owner_and_are_detached(self):
        value = dict(position=27.5, playing=True)
        self.registry.setValue('events', 'one', value)
        value['position'] = 300
        self.assertEqual(self.registry.getValue('events', 'one'), dict(position=27.5, playing=True))
        self.assertEqual(self.changes, [])

    def test_invalid_timeline_never_reaches_owner(self):
        for value in (None, 25, {}, dict(position=-1, playing=False),
                      dict(position=101, playing=False), dict(position=float('nan'), playing=False),
                      dict(position=True, playing=False), dict(position=10, playing='yes')):
            self.assertFalse(self.registry.changeValue('events', 'one', value))
        self.assertEqual(self.changes, [])

    def test_replay_and_pause_are_delivered_without_changing_position(self):
        self.registry.setValue('events', 'one', dict(position=100, playing=False))
        self.assertTrue(self.registry.changeValue('events', 'one', dict(position=100, playing=True)))
        self.assertEqual(self.changes, [('one', dict(position=100, playing=True))])


if __name__ == '__main__':
    unittest.main()
