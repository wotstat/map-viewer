"""Viewer lifecycle. Listeners receive (event, immutable ViewerContext).

ready: geometry and HUD usable; stopping: remove models synchronously while
the space exists; stopped: return finished. getContext is None outside ready.
"""
import logging
from collections import namedtuple

ViewerContext = namedtuple('ViewerContext', 'spaceID arenaID geometryName gameplayID visibilityMask')
log = logging.getLogger('WOTSTAT_LOCAL_MAPS')
_listeners = []
_context = None


def subscribe(listener):
    if not callable(listener):
        raise ValueError('Listener must be callable')
    if listener not in _listeners:
        _listeners.append(listener)


def unsubscribe(listener):
    if listener in _listeners:
        _listeners.remove(listener)


def getContext():
    return _context


def _emit(event, context):
    global _context
    _context = context if event == 'ready' else None
    for listener in tuple(_listeners):
        try:
            listener(event, context)
        except Exception:
            log.exception('Viewer lifecycle listener failed: %s', event)
