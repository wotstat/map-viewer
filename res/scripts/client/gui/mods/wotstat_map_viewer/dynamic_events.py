# coding: utf-8
"""Local WoT scenario timelines; the root sequence owns child timing/activation."""
import logging
import math

from . import debug_panel
from .localization import text

log = logging.getLogger('WOTSTAT_MAP_VIEWER')
SECTION = 'wotstat.map-viewer.dynamic-events'
INTERVAL = 0.05


class DynamicEvent(object):
    def __init__(self, eventID, gameObject, sequence):
        self.id = eventID
        self.gameObject = gameObject
        self.duration = float(sequence.duration)
        self.wasActive = bool(gameObject.isActive)
        self.pendingTime = None
        self.pendingSince = None
        self.playing = False
        self.position = 0.0

    def value(self):
        return dict(position=self.position, playing=self.playing)


class DynamicEvents(object):
    def __init__(self, spaceID, arena, minimap):
        self.spaceID = spaceID
        self.arena = arena
        self.minimap = minimap
        self.events = {}
        self.changers = []
        self._callback = None
        self._stopped = False
        self._registered = False

    def start(self):
        # This feature is scoped to WoT EU. Do not import its native component
        # types into the MT client, even when a map has similarly named objects.
        from constants import AUTH_REALM
        if AUTH_REALM != 'EU' or self.arena.geometryName.endswith(('_sm24', '_sm25')):
            return
        import BigWorld
        import CGF
        from GenericComponents import Sequence
        from UIComponents import MinimapChangerComponent
        self._sequenceType = Sequence
        self._changerType = MinimapChangerComponent
        objects = []
        queue = CGF.CommandQueue(self.spaceID)
        queue.manager.each(objects.append)
        for go in objects:
            name = unicode(go.name).rsplit('/', 1)[-1]
            if name.endswith('.prefab'):
                name = name[:-7]
            if not name.endswith('_scenario'):
                continue
            sequence = go.findRead(Sequence)
            if sequence is None:
                continue
            duration = float(sequence.duration)
            if duration <= 0 or math.isnan(duration) or math.isinf(duration):
                continue
            eventID = name[:-9]
            if eventID in self.events:
                log.warning('Duplicate dynamic scenario: %s', eventID)
                continue
            self.events[eventID] = DynamicEvent(eventID, go, sequence)
        if not self.events:
            return
        layers = getattr(self.arena, 'minimapLayers', {}) or {}
        # Component names need not match the scenario ID (Prokhorovka uses
        # planeCrash vs planesCrash). The native layerId is the actual link.
        for go in objects:
            changer = go.findRead(MinimapChangerComponent)
            if changer is not None and changer.layerId in layers:
                self.changers.append(go)
        self.minimap.setEventLayers(layers)
        controls = []
        for number, eventID in enumerate(sorted(self.events), 1):
            event = self.events[eventID]
            if not event.wasActive:
                queue.activateGameObject(event.gameObject)
            self._request(event, 0.0, False)
            controls.append(dict(id=eventID, type='timeline',
                label=text('dynamicEventName') % (number, eventID), value=event.value(),
                playTooltip=text('eventPlay'), pauseTooltip=text('eventPause')))
        debug_panel.registerSection(SECTION, text('dynamicEvents'), controls, self.change)
        self._registered = True
        self._callback = BigWorld.callback(INTERVAL, self._tick)
        log.info('Dynamic events ready: %s', ', '.join(sorted(self.events)))

    def change(self, eventID, value):
        event = self.events[eventID]
        position = float(value['position'])
        playing = value['playing']
        if playing and position >= 100:
            position = 0.0
        self._request(event, position, playing)

    def _request(self, event, position, playing):
        import BigWorld
        sequence = event.gameObject.findWrite(self._sequenceType)
        if sequence is None:
            raise RuntimeError('Dynamic scenario sequence disappeared: %s' % event.id)
        sequence.pause()
        event.pendingTime = event.duration * position / 100.0
        event.pendingSince = BigWorld.time()
        event.position = position
        event.playing = playing
        sequence.requestTime(event.pendingTime)

    def _tick(self):
        import BigWorld
        self._callback = None
        if self._stopped:
            return
        try:
            for event in self.events.values():
                sequence = event.gameObject.findWrite(self._sequenceType)
                if sequence is None:
                    raise RuntimeError('Dynamic scenario sequence disappeared: %s' % event.id)
                if event.pendingTime is not None:
                    # Both requestTime and start are applied by the next CGF
                    # update. Never overwrite a drag with an old sequence time.
                    if abs(float(sequence.time) - event.pendingTime) > 0.02:
                        if BigWorld.time() - event.pendingSince > 3.0:
                            raise RuntimeError('Dynamic scenario seek timed out: %s' % event.id)
                        continue
                    event.pendingTime = event.pendingSince = None
                    if event.playing:
                        sequence.start()
                else:
                    event.position = max(0.0, min(100.0, float(sequence.time) * 100.0 / event.duration))
                    if event.playing and event.position >= 99.999:
                        sequence.pause()
                        event.position = 100.0
                        event.playing = False
                debug_panel.setValue(SECTION, event.id, event.value())
            visible = set()
            for go in self.changers:
                if go.valid and go.isActive:
                    changer = go.findRead(self._changerType)
                    if changer is not None:
                        visible.add(unicode(changer.layerId))
            self.minimap.setEventLayerVisibility(visible)
        except Exception:
            log.exception('Dynamic event playback failed')
            self.stop()
            return
        self._callback = BigWorld.callback(INTERVAL, self._tick)

    def stop(self):
        import BigWorld
        self._stopped = True
        if self._callback is not None:
            BigWorld.cancelCallback(self._callback)
            self._callback = None
        if self._registered:
            debug_panel.unregisterSection(SECTION)
            self._registered = False
        from .cleanup import CleanupStack
        cleanup = CleanupStack()
        if self.minimap is not None:
            cleanup.defer('clear dynamic minimap layers', self.minimap.clearEventLayers)
        for event in self.events.values():
            cleanup.defer('pause dynamic scenario ' + event.id, self._releaseEvent, event)
        errors = cleanup.run()
        self.events.clear()
        self.changers = []
        self.minimap = self.arena = None
        for name, error in errors:
            log.error('Dynamic event cleanup failed at %s: %s', name, error)
        if errors:
            raise RuntimeError('Dynamic event cleanup failed')

    def _releaseEvent(self, event):
        import CGF
        if event.gameObject.valid:
            sequence = event.gameObject.findWrite(self._sequenceType)
            if sequence is not None:
                sequence.pause()
            if not event.wasActive:
                CGF.CommandQueue(self.spaceID).deactivateGameObject(event.gameObject)
        event.gameObject = None
