import os
import sys
import unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'res', 'scripts', 'client', 'gui', 'mods'))
from wotstat_local_maps import events


class LifecycleTest(unittest.TestCase):
    def test_listener_failures_and_unsubscribe_do_not_break_cleanup_delivery(self):
        received = []
        context = events.ViewerContext(7, 23, 'map', 1, 31)
        def fail(event, ctx):
            raise RuntimeError('Broken external mod')
        def observe(event, ctx):
            received.append((event, ctx, events.getContext()))
        events.subscribe(fail)
        events.subscribe(observe)
        events.subscribe(observe)
        try:
            events._emit('ready', context)
            self.assertIs(events.getContext(), context)
            events._emit('stopping', context)
            self.assertIsNone(events.getContext())
            events.unsubscribe(observe)
            events._emit('stopped', context)
            self.assertEqual(received, [('ready', context, context), ('stopping', context, None)])
            with self.assertRaises(AttributeError):
                context.spaceID = 999
        finally:
            events.unsubscribe(fail)
            events.unsubscribe(observe)


if __name__ == '__main__':
    unittest.main()
