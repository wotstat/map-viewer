# coding: utf-8
import logging
import math
import BigWorld
import GUI
import Math
import Keys
import ArenaType
from constants import AUTH_REALM
from helpers import dependency
from skeletons.gui.shared.utils import IHangarSpace
from CurrentVehicle import g_currentVehicle
from SpaceVisibilityFlags import SpaceVisibilityFlagsFactory
from gui.Scaleform.daapi.view.meta.MinimapMeta import MinimapMeta
from gui.Scaleform.daapi.view.battle.shared.ingame_menu import IngameMenu
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.Scaleform.daapi.view.battle.shared.minimap.settings import TRANSFORM_FLAG
from .minimap_bounds import getMinimapBounds
from .localization import text

log = logging.getLogger('WOTSTAT_MAP_VIEWER')

class LocalSession(object):
    def __init__(self):
        self.active = False
        self.restoring = False
        self.paused = False
        self.camera = None
        self.flight = None
        self._cameraSpeed = 60.0
        self.arena = None
        self.isHangar = False
        self.spaceID = None
        self._space = None
        self.mappingID = None
        self._callback = None
        self._saved = None
        self.battleApp = None
        self.hud = None
        self._hudRequested = False
        self._cleanup = None
        self.lastReport = None
        self._hangarReleased = False
        self._nativeHangar = False
        self._nativePathChanged = False
        self._nativeOverride = None
        self._restoreCallback = None
        self._loading = None
        self.stopping = False
        self.border = None
        self._loadingWatchdog = None
        self._restoreAllowed = True
        self.cursorControl = False
        self.minimapVisible = True
        self.interfaceVisible = True
        self._ctrlKeys = set()
        self._eventContext = None
        self.visibilityMask = None
        self.dynamicEvents = None

    def start(self, arenaID):
        from . import bootstrap as ui
        from .cleanup import CleanupStack
        from .catalog import HangarArena, isHangarKey
        if self.active or self.restoring:
            return
        hangar = dependency.instance(IHangarSpace)
        if not hangar.spaceInited or BigWorld.player().__class__.__name__ != 'PlayerAccount' or not g_currentVehicle.item:
            return
        self.isHangar = isHangarKey(arenaID)
        self._nativeHangar = self.isHangar and AUTH_REALM == 'EU'
        self.arenaID = None if self.isHangar else int(arenaID)
        self.arena = HangarArena(arenaID.split(':', 1)[1]) if self.isHangar else ArenaType.g_cache[self.arenaID]
        lobby = ui.findView('lobby')
        lobbyApp = ui.app()
        self._saved = dict(camera=BigWorld.camera(), fov=BigWorld.projection().fov,
                           cursorVisible=GUI.mcursor().visible, cursorClipped=GUI.mcursor().clipped,
                           spaceID=hangar.spaceID, vehicleCD=g_currentVehicle.item.intCD,
                           path=hangar.spacePath, environment=getattr(hangar, 'environment', None),
                           mask=hangar.visibilityMask, premium=hangar._HangarSpace__isSpacePremium,
                           account=BigWorld.player(), lobby=lobby, app=lobbyApp,
                           appActive=lobbyApp.isActive, cursorMode=lobbyApp.ctrlModeFlags,
                           optimizer=lobbyApp.graphicsOptimizationManager.getEnable())
        self._cleanup = CleanupStack()
        self._hudRequested = False
        self._hangarReleased = False
        self._nativePathChanged = False
        self._nativeOverride = None
        self._started = self._lastTick = BigWorld.time()
        self.active = True
        self.stopping = False
        self._restoreAllowed = True
        self.cursorControl = self.paused = False
        self.minimapVisible = not self.isHangar
        self.interfaceVisible = True
        self._ctrlKeys.clear()
        self._showLoading(self._beginStart)

    def _showLoading(self, action):
        from .loading import LoadingCover
        self._hideLoading()
        try:
            self._loading = LoadingCover(lambda: self._runLoadingAction(action))
            self._loadingWatchdog = BigWorld.callback(10.0, self._loadingFailed)
        except Exception:
            log.exception('Loading screen creation failed')
            self._hideLoading()
            self._stopNow()

    def _runLoadingAction(self, action):
        if self._loadingWatchdog is not None:
            BigWorld.cancelCallback(self._loadingWatchdog)
            self._loadingWatchdog = None
        action()

    def _loadingFailed(self):
        self._loadingWatchdog = None
        log.error('Loading screen initialization timed out')
        self._hideLoading()
        self._stopNow()

    def _hideLoading(self):
        if self._loadingWatchdog is not None:
            BigWorld.cancelCallback(self._loadingWatchdog)
            self._loadingWatchdog = None
        if self._loading:
            self._loading.close()
            self._loading = None

    def _beginStart(self):
        if self._nativeHangar:
            self._beginNativeHangar()
        else:
            self._openView()

    def _beginNativeHangar(self):
        from gui import ClientHangarSpace

        if BigWorld.player() is not self._saved['account']:
            self.stop()
            return
        try:
            self._cleanup.defer('restore original hangar', self._restoreNativeHangar)
            hangar = dependency.instance(IHangarSpace)
            path = 'spaces/' + self.arena.geometryName
            if hangar.spacePath != path:
                self._ensureNativeHangarConfig(path)
                # The EU hangar has its own camera, entities and CGF scripts.
                # Mapping its geometry into a regular space crashes those scripts.
                premium = hangar.isPremium
                overrides = ClientHangarSpace._EVENT_HANGAR_PATHS
                self._nativeOverride = (premium, overrides.get(premium))
                self._nativePathChanged = True
                self._hangarReleased = True
                ClientHangarSpace.g_clientHangarSpaceOverride.setPath(path, isPremium=premium)
                self._switchStarted = BigWorld.time()
                self._callback = BigWorld.callback(0.1, self._waitSelectedHangar)
            else:
                self._openView()
        except Exception:
            log.exception('Native hangar switch failed')
            self.stop()

    def _ensureNativeHangarConfig(self, path):
        from gui import ClientHangarSpace
        from gui.hangar_config import HangarConfig
        import ResMgr

        key = path.lower()
        if key in ClientHangarSpace._HANGAR_CFGS:
            return
        settings = ResMgr.openSection(path + '/space.settings/hangarSettings')
        defaults = ResMgr.openSection('gui/hangars.xml')
        if settings is None or defaults is None:
            raise ValueError('Hangar configuration is unavailable: %s' % path)
        config = HangarConfig()
        config.loadDefaultHangarConfig(defaults, ClientHangarSpace._IGR_HANGAR_PATH_KEY)
        config.loadConfig(settings)
        ClientHangarSpace._loadVisualScript(config, settings)
        for sectionName, loader in (('customizationHangarSettings', 'loadCustomizationConfig'),
                                    ('secondaryHangarSettings', 'loadSecondaryConfig')):
            section = settings[sectionName]
            if section is not None:
                extra = HangarConfig()
                getattr(extra, loader)(section)
                config[sectionName] = extra
        ClientHangarSpace._HANGAR_CFGS[key] = config

    def _waitSelectedHangar(self):
        self._callback = None
        if not self.active or self.stopping:
            return
        hangar = dependency.instance(IHangarSpace)
        if BigWorld.player() is not self._saved['account']:
            self.stop()
        elif hangar.spaceInited and hangar.isModelLoaded and hangar.spacePath == 'spaces/' + self.arena.geometryName:
            self._openView()
        elif BigWorld.time() - self._switchStarted > 90:
            log.error('Selected hangar did not become ready within 90 seconds')
            self.stop()
        else:
            self._callback = BigWorld.callback(0.1, self._waitSelectedHangar)

    def _openView(self):
        from . import bootstrap as ui
        from .battle_app import LocalBattleApp
        from .flight import FlightController
        from PlayerEvents import g_playerEvents
        hangar = dependency.instance(IHangarSpace)
        lobby, lobbyApp = self._saved['lobby'], self._saved['app']
        cleanup = self._cleanup
        if BigWorld.player() is not self._saved['account']:
            self.stop()
            return
        try:
            if not self._nativeHangar:
                cleanup.defer('reload original hangar', self._restoreHangar)
            cleanup.defer('restore lobby rendering', self._restoreLobby)
            lobby.getParentWindow().hide()
            lobbyApp.setVisible(False)
            lobbyApp.active(False)
            cleanup.defer('restore lobby optimizer', lobbyApp.graphicsOptimizationManager.switchOptimizationEnabled, self._saved['optimizer'])
            lobbyApp.graphicsOptimizationManager.switchOptimizationEnabled(False)
            if self._nativeHangar:
                self.spaceID = hangar.spaceID
                mask = hangar.visibilityMask
            else:
                # Battle terrain needs a regular space after releasing the
                # native hangar. WoT returns a handle; MT returns an ID.
                self._hangarReleased = True
                hangar.destroy()
                self._space = BigWorld.createSpace()
                self.spaceID = getattr(self._space, 'id', self._space)
                cleanup.defer('release local space', BigWorld.releaseSpace, self.spaceID)
                cleanup.defer('clear local space', BigWorld.clearSpace, self.spaceID)
            if self.isHangar and not self._nativeHangar:
                from gui.ClientHangarSpace import getHangarFullVisibilityMask
                mask = getHangarFullVisibilityMask('spaces/' + self.arena.geometryName)
            elif not self.isHangar:
                flags = SpaceVisibilityFlagsFactory.create(self.arena.geometryName)
                mask = flags.getMaskForGameplayID(self.arena.gameplayID)
            self.visibilityMask = mask
            if not self._nativeHangar:
                self.mappingID = BigWorld.addSpaceGeometryMapping(self.spaceID, None, 'spaces/' + self.arena.geometryName, mask)
                cleanup.defer('remove local geometry', BigWorld.delSpaceGeometryMapping, self.spaceID, self.mappingID)
            self.camera = BigWorld.FreeCamera()
            self.camera.spaceID = self.spaceID
            bl, tr = self.arena.boundingBox
            center = (bl + tr) * 0.5
            position = self.arena.startPosition if self.isHangar else (center.x, 140.0, center.y - 250.0)
            self.flight = FlightController(self.camera, position, self._cameraSpeed)
            cleanup.defer('restore hangar camera', self._restoreCamera)
            BigWorld.camera(self.camera)
            cleanup.defer('restore shadow camera mode', BigWorld.enableFreeCameraModeForShadowManager, False)
            BigWorld.enableFreeCameraModeForShadowManager(True)
            cleanup.defer('restore FOV', setattr, BigWorld.projection(), 'fov', self._saved['fov'])
            BigWorld.projection().fov = math.radians(70.0)
            cleanup.defer('restore cursor visibility', setattr, GUI.mcursor(), 'visible', self._saved['cursorVisible'])
            cleanup.defer('restore cursor clipping', setattr, GUI.mcursor(), 'clipped', self._saved['cursorClipped'])
            GUI.mcursor().visible = False
            GUI.mcursor().clipped = True
            self.battleApp = LocalBattleApp()
            cleanup.defer('close battle UI', self.battleApp.close)
            from .ui_routing import routeCommonWindows
            routeCommonWindows(self.battleApp, cleanup)
            self.battleApp.active(True)
            g_playerEvents.onAccountBecomeNonPlayer += self._abort
            g_playerEvents.onDisconnected += self._abort
            cleanup.defer('remove lifecycle listeners', self._removeListeners)
            self._callback = BigWorld.callback(0.0, self._tick)
            log.info('Loading geometry=%s mode=%s space=%s; Account retained', self.arena.geometryName, self.arena.gameplayName, self.spaceID)
        except Exception:
            log.exception('Local space creation failed')
            self.stop()

    def _restoreCamera(self):
        if not self._hangarReleased and dependency.instance(IHangarSpace).spaceID == self._saved['spaceID']:
            BigWorld.camera(self._saved['camera'])
        elif BigWorld.camera() is self.camera:
            BigWorld.camera(BigWorld.FreeCamera())

    def _restoreHangar(self):
        if self._restoreAllowed and self._hangarReleased and BigWorld.player() is self._saved['account']:
            self.restoring = True
            self._restoreStarted = BigWorld.time()
            hangar = dependency.instance(IHangarSpace)
            try:
                if not hangar.inited:
                    hangar.init(self._saved['premium'])
                self._restoreCallback = BigWorld.callback(0.1, self._waitHangar)
            except Exception:
                self.restoring = False
                raise

    def _restoreNativeHangar(self):
        if not self._nativePathChanged or not self._restoreAllowed or BigWorld.player() is not self._saved['account']:
            return
        from gui import ClientHangarSpace

        premium, original = self._nativeOverride
        overrides = ClientHangarSpace._EVENT_HANGAR_PATHS
        if original is None:
            overrides.pop(premium, None)
        else:
            overrides[premium] = original
        self.restoring = True
        self._restoreStarted = BigWorld.time()
        hangar = dependency.instance(IHangarSpace)
        try:
            hangar.refreshSpace(self._saved['premium'], True)
            hangar.onSpaceChanged()
            self._restoreCallback = BigWorld.callback(0.1, self._waitHangar)
        except Exception:
            self.restoring = False
            raise

    def _waitHangar(self):
        self._restoreCallback = None
        hangar = dependency.instance(IHangarSpace)
        saved = self._saved
        if BigWorld.player() is not saved['account']:
            self._finishReturn(False)
        elif hangar.spaceInited and hangar.isModelLoaded:
            self._finishReturn(True)
        elif BigWorld.time() - self._restoreStarted > 90:
            log.error('Original hangar did not become ready within 90 seconds')
            self._finishReturn(False)
        else:
            self._restoreCallback = BigWorld.callback(0.1, self._waitHangar)

    def _finishReturn(self, ready):
        saved = self._saved
        hangar = dependency.instance(IHangarSpace)
        self.lastReport.update(hangarReady=ready,
            sameAccount=BigWorld.player() is saved['account'],
            sameHangar=hangar.spacePath == saved['path'],
            sameEnvironment=getattr(hangar, 'environment', None) == saved['environment'],
            sameVisibility=hangar.visibilityMask == saved['mask'],
            sameVehicle=bool(g_currentVehicle.item and g_currentVehicle.item.intCD == saved['vehicleCD']))
        self.restoring = False
        self._hideLoading()
        self._saved = None
        log.info('Returned: %s', self.lastReport)
        if self._eventContext is not None:
            from . import events
            context, self._eventContext = self._eventContext, None
            events._emit('stopped', context)

    def notifyReady(self):
        if self._eventContext is None and self.active and not self.stopping:
            from .dynamic_events import DynamicEvents
            from .bootstrap import MINIMAP
            if not self.isHangar:
                self.dynamicEvents = DynamicEvents(self.spaceID, self.arena, self.hud.getComponent(MINIMAP))
                self._cleanup.defer('stop dynamic events', self._stopDynamicEvents)
                try:
                    self.dynamicEvents.start()
                except Exception:
                    log.exception('Dynamic event initialization failed')
                    self._stopDynamicEvents()
            from . import events
            self._eventContext = events.ViewerContext(self.spaceID, self.arenaID,
                self.arena.geometryName, self.arena.gameplayID, self.visibilityMask)
            events._emit('ready', self._eventContext)

    def _stopDynamicEvents(self):
        controller, self.dynamicEvents = self.dynamicEvents, None
        if controller is not None:
            controller.stop()

    def _restoreLobby(self):
        if not self._restoreAllowed:
            return
        saved = self._saved
        if saved['lobby'] and not saved['lobby'].isDisposed():
            saved['lobby'].getParentWindow().show()
        if saved['app'].component is not None:
            saved['app'].active(saved['appActive'])
            saved['app'].setVisible(True)
            saved['app'].syncCursor(saved['cursorMode'])

    def _removeListeners(self):
        from PlayerEvents import g_playerEvents
        g_playerEvents.onAccountBecomeNonPlayer -= self._abort
        g_playerEvents.onDisconnected -= self._abort

    def _abort(self, *args):
        # Account/application transitions must release local resources before
        # the native transition clears worlds. Only user exit is animated.
        self._restoreAllowed = False
        self._hideLoading()
        if self.active:
            self._stopNow()

    def _tick(self):
        from . import bootstrap as ui
        self._callback = None
        if not self.active or self.stopping:
            return
        try:
            now = BigWorld.time()
            if BigWorld.player() is not self._saved['account']:
                self.stop()
                return
            if BigWorld.spaceLoadStatus() >= 0.99:
                BigWorld.worldDrawEnabled(True)
            if not self._hudRequested and BigWorld.spaceLoadStatus() >= 0.99 and BigWorld.virtualTextureRenderComplete() and self.battleApp.initialized:
                from .border import LocalArenaBorder
                if not self.isHangar:
                    self.border = LocalArenaBorder()
                    self._cleanup.defer('release arena border', self.border.stopControl)
                    self.border.attach(self.spaceID, self.arena.boundingBox)
                self._hudRequested = True
                self.battleApp.loadView(SFViewLoadParams(ui.HUD))
            if self.hud is None and now - self._started > 90:
                raise RuntimeError('Map or native HUD loading timed out')
            if self.hud and not self.paused:
                self.flight.update(now - self._lastTick)
            self._lastTick = now
            self._callback = BigWorld.callback(0.0, self._tick)
        except Exception:
            log.exception('Local viewer update failed')
            self.stop()

    def pause(self):
        self.paused = True
        self._syncInputMode()

    def resume(self):
        if not self.active:
            return
        self.paused = False
        self._syncInputMode()

    def _syncInputMode(self, preserveInertia=False):
        from gui import GUI_CTRL_MODE_FLAG
        wasVisible = GUI.mcursor().visible
        self.cursorControl = bool(self._ctrlKeys) and not self.paused and not self.stopping
        visible = self.paused or self.cursorControl
        if self.flight:
            self.flight.clear(stopMotion=not preserveInertia)
        if self.border:
            self.border.extended(False)
        self._lastTick = BigWorld.time()
        if self.hud:
            self.hud.flashObject.as_setInteractive(self.cursorControl)
        if self.battleApp:
            if (not visible or not wasVisible) and self.battleApp.cursorMgr is not None:
                # The stock manager resets both the device and Flash cursor,
                # including its saved position for the next attach/detach.
                self.battleApp.cursorMgr.resetMousePosition()
            self.battleApp.syncCursor(GUI_CTRL_MODE_FLAG.GUI_ENABLED if visible else GUI_CTRL_MODE_FLAG.CURSOR_ATTACHED)
        GUI.mcursor().visible = visible
        GUI.mcursor().clipped = not visible

    def releaseInput(self):
        self._ctrlKeys.clear()
        self._syncInputMode()

    def handleMouse(self, event):
        if self.stopping or self.hud is None:
            return True
        if self.paused or self.cursorControl:
            GUI.handleMouseEvent(event)
        else:
            self.flight.mouse(event)
            self._cameraSpeed = self.flight.speed
            # Same recentering as AvatarInputHandler.VideoCamera: retain mouse
            # deltas for rotation but never accumulate a hidden cursor position.
            GUI.mcursor().position = (0.0, 0.0)
        return True

    def handleKey(self, event, original):
        from . import bootstrap as ui
        if event.key in (Keys.KEY_LCONTROL, Keys.KEY_RCONTROL):
            if event.isRepeatedEvent():
                return True
            if event.isKeyDown():
                self._ctrlKeys.add(event.key)
            else:
                self._ctrlKeys.discard(event.key)
            if self.hud and not self.stopping:
                self._syncInputMode(preserveInertia=not self.paused)
                if self.paused:
                    GUI.handleKeyEvent(event)
            return True
        if self.stopping or self.hud is None:
            return True
        if self.paused:
            # Keep native key capture and top-window focus handling.
            # Settings/dialogs stay paused; the native menu owns resume.
            GUI.handleKeyEvent(event)
            return True
        if event.key == Keys.KEY_ESCAPE:
            if not event.isKeyDown() or event.isRepeatedEvent():
                return True
            self.pause()
            self.battleApp.loadView(SFViewLoadParams(ui.MENU))
            return True
        if event.key in (Keys.KEY_M, Keys.KEY_V):
            if event.isKeyDown() and not event.isRepeatedEvent():
                if event.key == Keys.KEY_M:
                    self.minimapVisible = not self.minimapVisible
                else:
                    self.interfaceVisible = not self.interfaceVisible
                self.hud.flashObject.as_setVisibility(self.interfaceVisible, self.minimapVisible)
            return True
        if self.cursorControl:
            GUI.handleKeyEvent(event)
            return True
        if event.isKeyDown() and event.key in (Keys.KEY_EQUALS, Keys.KEY_MINUS):
            if self.hud:
                self.hud.flashObject.as_resizeMinimap(1 if event.key == Keys.KEY_EQUALS else -1)
            return True
        self.flight.key(event)
        self._cameraSpeed = self.flight.speed
        if event.key in (Keys.KEY_LALT, Keys.KEY_RALT) and self.border:
            self.border.extended(bool(self.flight.keys.intersection((Keys.KEY_LALT, Keys.KEY_RALT))))
        return True

    def stop(self):
        if not self.active or self.stopping:
            return
        self.stopping = True
        self._ctrlKeys.clear()
        self._syncInputMode()
        if self.flight:
            self.flight.clear()
        self._showLoading(self._stopNow)

    def _stopNow(self):
        if not self.active:
            return
        self.active = False
        if self._eventContext is not None:
            from . import events
            events._emit('stopping', self._eventContext)
        if self._callback is not None:
            BigWorld.cancelCallback(self._callback)
            self._callback = None
        saved = self._saved
        if self.flight:
            self.flight.clear()
        self.lastReport = dict(cleanupErrors=0)
        errors = self._cleanup.run()
        for name, error in errors:
            log.error('Cleanup failed at %s: %s', name, error)
        self.battleApp = self.hud = self.flight = self.camera = None
        self.border = None
        self.spaceID = self.mappingID = None
        self._space = None
        self.visibilityMask = None
        self.paused = False
        self.cursorControl = False
        self._ctrlKeys.clear()
        self.stopping = False
        self.lastReport['cleanupErrors'] = len(errors)
        if not self.restoring:
            self._finishReturn(not self._hangarReleased)
        self._cleanup = None

class LocalMinimap(MinimapMeta):
    def __init__(self):
        super(LocalMinimap, self).__init__()
        self.native = None
        self.entries = []
        self._eventLayers = {}

    def onMinimapClicked(self, *args):
        pass

    def applyNewSize(self, sizeIndex):
        pass

    def attach(self, path, arena):
        from . import bootstrap as ui
        factory = getattr(GUI, 'MinimapFlashAS3', None)
        inputMode = 'inputKeyMode'
        if factory is None:
            factory = GUI.WGMinimapFlashAS3
            inputMode = 'wg_inputKeyMode'
            self.as_disableHintPanelS()
        else:
            self.as_disableHintPanelS(True)
        self.native = factory(self.app.movie, path)
        setattr(self.native, inputMode, 2)
        self.app.component.addChild(self.native, 'wotstatLocalMap')
        self.native.setArenaBB(*getMinimapBounds(arena.boundingBox))
        self.native.mapSize = Math.Vector2(210.0, 210.0)
        import ResMgr
        self.as_setBackgroundS('img://' + arena.minimap if arena.minimap and ResMgr.isFile(arena.minimap) else '')
        from .minimap_points import iterTeamPoints
        from gui.Scaleform.daapi.view.battle.shared.points_of_interest.constants import POI_TYPE_UI_MAPPING
        from gui.Scaleform.genConsts.POI_CONSTS import POI_CONSTS
        for symbol, position, number in iterTeamPoints(
                arena.teamBasePositions, arena.teamSpawnPoints, arena.controlPoints):
            entry = self.addPoint(symbol, position)
            self.native.entryInvoke(entry, ('setPointNumber', number))
            if symbol not in ('AllyTeamSpawnEntry', 'EnemyTeamSpawnEntry'):
                self.native.entryInvoke(entry, ('setState', 'default'))
        for point in arena.pointsOfInterest or ():
            entry = self.addPoint('PoiMinimapEntry', point['position'])
            self.native.entryInvoke(entry, ('setType', POI_TYPE_UI_MAPPING[point['type']]))
            self.native.entryInvoke(entry, ('setStatus', POI_CONSTS.POI_STATUS_ACTIVE))
            self.native.entryInvoke(entry, ('setIsAlly', False))
        entry = self.native.addEntry('VideoCameraEntry', 'personal', ui.session.camera.invViewMatrix, True, TRANSFORM_FLAG.DEFAULT)
        self.entries.append(entry)
        log.info('Native minimap attached path=%s entries=%s', path, len(self.entries))

    def addPoint(self, symbol, position):
        matrix = Math.Matrix()
        matrix.setTranslate((position[0], 0.0, position[1]))
        entry = self.native.addEntry(symbol, 'points', matrix, True, TRANSFORM_FLAG.DEFAULT)
        self.entries.append(entry)
        return entry

    def setEventLayers(self, layers):
        from gui.Scaleform.genConsts.BATTLE_MINIMAP_CONSTS import BATTLE_MINIMAP_CONSTS
        from constants import MinimapLayerType
        import ResMgr
        self.clearEventLayers()
        types = {MinimapLayerType.BASE: BATTLE_MINIMAP_CONSTS.SCENARIO_EVENT_EFFECT,
                 MinimapLayerType.ALERT: BATTLE_MINIMAP_CONSTS.SCENARIO_EVENT_ALERT}
        for layerID, (path, layerType) in sorted(layers.items()):
            if layerType in types and ResMgr.isFile(path):
                self.as_setScenarioEventS(layerID, 'img://' + path, types[layerType])
                self.as_setScenarioEventVisibleS(layerID, False)
                self._eventLayers[layerID] = False

    def setEventLayerVisibility(self, visible):
        for layerID, previous in self._eventLayers.items():
            current = layerID in visible
            if previous != current:
                self.as_setScenarioEventVisibleS(layerID, current)
                self._eventLayers[layerID] = current

    def clearEventLayers(self):
        for layerID in self._eventLayers:
            self.as_clearScenarioEventS(layerID)
        self._eventLayers.clear()

    def _dispose(self):
        self.clearEventLayers()
        if self.native is not None:
            for entry in self.entries:
                self.native.delEntry(entry)
            self.app.component.delChild(self.native)
        self.native = None
        self.entries = []
        super(LocalMinimap, self)._dispose()

class LocalMenu(IngameMenu):
    def settingsClick(self):
        from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
        self.app.loadView(SFViewLoadParams(VIEW_ALIAS.SETTINGS_WINDOW), ctx=dict(
            redefinedKeyMode=True, tabIndex=None, isBattleSettings=True))

    def quitBattleClick(self):
        from .bootstrap import session
        # Finish the native button's input/logging dispatch before closing
        # its entire movie and the managers used by that dispatch.
        BigWorld.callback(0.0, session.stop)

    def helpClick(self):
        pass

    def cancelClick(self):
        from .bootstrap import session
        self.destroy()
        session.resume()

    def onWindowClose(self):
        self.cancelClick()

    def _setMenuButtonsLabels(self):
        self.as_setMenuButtonsLabelsS('', text('settings'), text('resume'), text('exitToHangar'))

    def _setMenuButtons(self):
        from gui.Scaleform.genConsts.INGAMEMENU_CONSTANTS import INGAMEMENU_CONSTANTS as buttons
        self.as_setMenuButtonsS([buttons.QUIT, buttons.SETTINGS, buttons.CANCEL])
