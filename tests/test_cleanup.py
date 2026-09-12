import os
import sys
import unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'res', 'scripts', 'client', 'gui', 'mods'))
from wotstat_map_viewer.cleanup import CleanupStack


class CleanupTest(unittest.TestCase):
    def test_failure_does_not_skip_camera_restore_or_release(self):
        calls = []
        cleanup = CleanupStack()
        cleanup.defer('release local space', calls.append, 'release')
        cleanup.defer('restore camera', calls.append, 'camera')
        def fail():
            calls.append('ui')
            raise ValueError('injected disposal failure')
        cleanup.defer('close UI', fail)
        errors = cleanup.run()
        self.assertEqual(calls, ['ui', 'camera', 'release'])
        self.assertEqual([name for name, error in errors], ['close UI'])
        self.assertEqual(cleanup.run(), [])
        self.assertEqual(calls, ['ui', 'camera', 'release'])


if __name__ == '__main__':
    unittest.main()
