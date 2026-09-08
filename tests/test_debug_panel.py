# coding: utf-8
import os
import sys
import unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'res', 'scripts', 'client', 'gui', 'mods'))
from wotstat_local_maps.debug_panel import SettingsRegistry


def slider(value=60):
    return dict(id='speed', type='slider', label=u'Скорость', value=value,
                min=5, max=500, step=1, suffix=u' м/с')


class DebugPanelTest(unittest.TestCase):
    def setUp(self):
        self.registry = SettingsRegistry()
        self.changes = []

    def test_sections_have_independent_control_ids_and_detached_data(self):
        controls = [slider()]
        self.registry.registerSection('camera', 'Camera', controls, lambda *v: self.changes.append(v))
        self.registry.registerSection('another.mod', 'Other', [slider(10)], lambda *v: None)
        controls[0]['value'] = 999
        snapshot = self.registry.snapshot()
        snapshot[0]['controls'][0]['value'] = 888
        self.assertTrue(self.registry.changeValue('camera', 'speed', 80))
        self.assertEqual(self.registry.getValue('camera', 'speed'), 80)
        self.assertEqual(self.registry.getValue('another.mod', 'speed'), 10)
        self.assertEqual(self.changes, [('speed', 80)])

    def test_programmatic_updates_notify_ui_without_callback_loop(self):
        events = []
        self.registry.subscribe(lambda *args: events.append(args))
        self.registry.registerSection('camera', 'Camera', [slider()], lambda *v: self.changes.append(v))
        self.registry.setValue('camera', 'speed', 75)
        self.registry.setValue('camera', 'speed', 75)
        self.assertEqual(events, [('sections',), ('value', 'camera', 'speed', 75)])
        self.assertEqual(self.changes, [])

    def test_rejected_registration_keeps_existing_section(self):
        self.registry.registerSection('camera', 'Original', [slider()], lambda *v: None)
        with self.assertRaises(ValueError):
            self.registry.registerSection('camera', 'Invalid', [slider(), slider()], lambda *v: None)
        self.assertEqual(self.registry.snapshot()[0]['title'], 'Original')

    def test_slider_bounds_and_non_finite_values_cannot_reach_callback(self):
        self.registry.registerSection('camera', 'Camera', [slider()], lambda *v: self.changes.append(v))
        for value in (4, 501, float('nan'), float('inf'), 10 ** 400, '60', True):
            self.assertFalse(self.registry.changeValue('camera', 'speed', value))
        self.assertEqual(self.registry.getValue('camera', 'speed'), 60)
        self.assertEqual(self.changes, [])

    def test_checkbox_and_dropdown_deliver_semantic_values(self):
        self.registry.registerSection('external', 'External', [
            dict(id='enabled', type='checkbox', label='Enabled', value=True),
            dict(id='quality', type='dropdown', label='Quality', value='low',
                 options=[dict(label='Low', value='low'), dict(label='High', value='high')])
        ], lambda *v: self.changes.append(v))
        self.assertTrue(self.registry.changeValue('external', 'enabled', False))
        self.assertTrue(self.registry.changeValue('external', 'quality', 'high'))
        self.assertFalse(self.registry.changeValue('external', 'quality', 'unknown'))
        self.assertFalse(self.registry.changeValue('external', 'enabled', 'false'))
        self.assertEqual(self.changes, [('enabled', False), ('quality', 'high')])

    def test_callback_failure_does_not_commit_value_or_break_other_sections(self):
        def fail(*args):
            raise RuntimeError('Rejected by the owner')
        self.registry.registerSection('broken', 'Broken', [slider()], fail)
        self.registry.registerSection('working', 'Working', [slider()], lambda *v: None)
        self.assertFalse(self.registry.changeValue('broken', 'speed', 100))
        self.assertEqual(self.registry.getValue('broken', 'speed'), 60)
        self.assertTrue(self.registry.changeValue('working', 'speed', 100))

    def test_unregister_releases_callback_and_stale_ui_events_are_ignored(self):
        self.registry.registerSection('camera', 'Camera', [slider()], lambda *v: self.changes.append(v))
        self.registry.unregisterSection('camera')
        self.registry.unregisterSection('camera')
        self.assertEqual(self.registry.snapshot(), [])
        self.assertFalse(self.registry.changeValue('camera', 'speed', 100))
        self.assertEqual(self.changes, [])


if __name__ == '__main__':
    unittest.main()
