# coding: utf-8
import logging
import math
import BigWorld
import GUI
import Math
import Keys
import ArenaType
from helpers import dependency
from skeletons.gui.shared.utils import IHangarSpace
from CurrentVehicle import g_currentVehicle
from SpaceVisibilityFlags import SpaceVisibilityFlagsFactory
from gui.Scaleform.daapi.view.meta.MinimapMeta import MinimapMeta
from gui.Scaleform.daapi.view.battle.shared.ingame_menu import IngameMenu
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.Scaleform.daapi.view.battle.shared.minimap.settings import TRANSFORM_FLAG
from .minimap_bounds import getMinimapBounds
from .debug_panel import g_registry

log = logging.getLogger('WOTSTAT_LOCAL_MAPS')

class LocalSession(object):
    def __init__(self):
        self.active = False
        self.restoring = False
        self.paused = False
        self.camera = None
        self.flight = None
        self.arena = None
        self.spaceID = None
        self.mappingID = None
        self._callback = None
        self._saved = None
        self.battleApp = None
        self.hud = None
        self._hudRequested = False
        self._cleanup = None
        self.lastReport = None
        self._hangarReleased = False
        self._restoreCallback = None
        self._loading = None
        self.stopping = False
        self.border = None
        self._loadingWatchdog = None
        self._restoreAllowed = True
        self.cursorControl = False
        self._ctrlKeys = set()

    def start(self, arenaID):
        from . import bootstrap as ui
        from .cleanup import CleanupStack
        if self.active or self.restoring:
            return
        hangar = dependency.instance(IHangarSpace)
        if not hangar.spaceInited or BigWorld.player().__class__.__name__ != 'PlayerAccount' or not g_currentVehicle.item:
            return
        self.arena = ArenaType.g_cache[int(arenaID)]
        lobby = ui.findView('lobby')
        lobbyApp = ui.app()
        self._saved = dict(camera=BigWorld.camera(), fov=BigWorld.projection().fov,
                           cursorVisible=GUI.mcursor().visible, cursorClipped=GUI.mcursor().clipped,
                           spaceID=hangar.spaceID, vehicleCD=g_currentVehicle.item.intCD,
                           path=hangar.spacePath, environment=hangar.environment,
                           mask=hangar.visibilityMask, premium=hangar._HangarSpace__isSpacePremium,
                           account=BigWorld.player(), lobby=lobby, app=lobbyApp,
                           appActive=lobbyApp.isActive, cursorMode=lobbyApp.ctrlModeFlags,
                           optimizer=lobbyApp.graphicsOptimizationManager.getEnable())
        self._cleanup = CleanupStack()
        self._hudRequested = False
        self._hangarReleased = False
        self._started = self._lastTick = BigWorld.time()
        self.active = True
        self.stopping = False
        self._restoreAllowed = True
        self.cursorControl = self.paused = False
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
            cleanup.defer('reload original hangar', self._restoreHangar)
            cleanup.defer('restore lobby rendering', self._restoreLobby)
            lobby.getParentWindow().hide()
            lobbyApp.setVisible(False)
            lobbyApp.active(False)
            cleanup.defer('restore lobby optimizer', lobbyApp.graphicsOptimizationManager.switchOptimizationEnabled, self._saved['optimizer'])
            lobbyApp.graphicsOptimizationManager.switchOptimizationEnabled(False)
            # Terrain/environment render state belongs to one active world.
            # Use the stock hangar lifecycle before mapping a battle space.
            self._hangarReleased = True
            hangar.destroy()
            # Default space is required for the battle terrain renderer. The
            # True flag used by ClientHangarSpace produces missing terrain here.
            self.spaceID = BigWorld.createSpace()
            cleanup.defer('release local space', BigWorld.releaseSpace, self.spaceID)
            cleanup.defer('clear local space', BigWorld.clearSpace, self.spaceID)
            flags = SpaceVisibilityFlagsFactory.create(self.arena.geometryName)
            mask = flags.getMaskForGameplayID(self.arena.gameplayID)
            self.mappingID = BigWorld.addSpaceGeometryMapping(self.spaceID, None, 'spaces/' + self.arena.geometryName, mask)
            cleanup.defer('remove local geometry', BigWorld.delSpaceGeometryMapping, self.spaceID, self.mappingID)
            self.camera = BigWorld.FreeCamera()
            self.camera.spaceID = self.spaceID
            bl, tr = self.arena.boundingBox
            center = (bl + tr) * 0.5
            self.flight = FlightController(self.camera, (center.x, 140.0, center.y - 250.0),
                                           g_registry.getValue('wotstat.free-camera', 'speed'))
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
            sameEnvironment=hangar.environment == saved['environment'],
            sameVisibility=hangar.visibilityMask == saved['mask'],
            sameVehicle=bool(g_currentVehicle.item and g_currentVehicle.item.intCD == saved['vehicleCD']))
        self.restoring = False
        self._hideLoading()
        self._saved = None
        log.info('Returned: %s', self.lastReport)

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
                self.border = LocalArenaBorder()
                self._cleanup.defer('release arena border', self.border.stopControl)
                self.border.attach(self.spaceID, self.arena.boundingBox)
                self._hudRequested = True
                self.battleApp.loadView(SFViewLoadParams(ui.HUD))
            if self.hud is None and now - self._started > 90:
                raise RuntimeError('Map or native HUD loading timed out')
            if self.hud and not self.paused and not self.cursorControl:
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

    def _syncInputMode(self):
        from gui import GUI_CTRL_MODE_FLAG
        self.cursorControl = bool(self._ctrlKeys) and not self.paused and not self.stopping
        visible = self.paused or self.cursorControl
        if self.flight:
            self.flight.clear()
        if self.border:
            self.border.extended(False)
        self._lastTick = BigWorld.time()
        if self.hud:
            self.hud.flashObject.as_setInteractive(self.cursorControl)
        if self.battleApp:
            self.battleApp.syncCursor(GUI_CTRL_MODE_FLAG.GUI_ENABLED if visible else GUI_CTRL_MODE_FLAG.CURSOR_ATTACHED)
        GUI.mcursor().visible = visible
        GUI.mcursor().clipped = not visible

    def releaseInput(self):
        self._ctrlKeys.clear()
        self._syncInputMode()

    def setCameraSpeed(self, controlID, value):
        if self.flight:
            self.flight.speed = float(value)

    def handleMouse(self, event):
        if self.stopping or self.hud is None:
            return True
        if self.paused or self.cursorControl:
            GUI.handleMouseEvent(event)
        else:
            oldSpeed = self.flight.speed
            self.flight.mouse(event)
            if self.flight.speed != oldSpeed:
                g_registry.setValue('wotstat.free-camera', 'speed', self.flight.speed)
        return True

    def handleKey(self, event, original):
        from . import bootstrap as ui
        if event.key in (Keys.KEY_LCONTROL, Keys.KEY_RCONTROL):
            if event.isKeyDown():
                self._ctrlKeys.add(event.key)
            else:
                self._ctrlKeys.discard(event.key)
            if self.hud and not self.stopping:
                self._syncInputMode()
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
        if self.cursorControl:
            GUI.handleKeyEvent(event)
            return True
        if event.isKeyDown() and event.key in (Keys.KEY_EQUALS, Keys.KEY_MINUS):
            if self.hud:
                self.hud.flashObject.as_resizeMinimap(1 if event.key == Keys.KEY_EQUALS else -1)
            return True
        self.flight.key(event)
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

    def onMinimapClicked(self, *args):
        pass

    def applyNewSize(self, sizeIndex):
        pass

    def attach(self, path, arena):
        from . import bootstrap as ui
        self.native = GUI.MinimapFlashAS3(self.app.movie, path)
        self.native.inputKeyMode = 2
        self.app.component.addChild(self.native, 'wotstatLocalMap')
        self.native.setArenaBB(*getMinimapBounds(arena.boundingBox))
        self.native.mapSize = Math.Vector2(210.0, 210.0)
        import ResMgr
        self.as_setBackgroundS('img://' + arena.minimap if arena.minimap and ResMgr.isFile(arena.minimap) else '')
        for team, bases in enumerate(arena.teamBasePositions or (), 1):
            for number, position in bases.iteritems():
                self.addPoint('AllyTeamBaseEntry' if team == 1 else 'EnemyTeamBaseEntry', position, number)
        for number, position in enumerate(arena.controlPoints or ()):
            self.addPoint('ControlPointEntry', position, number)
        entry = self.native.addEntry('VideoCameraEntry', 'personal', ui.session.camera.invViewMatrix, True, TRANSFORM_FLAG.DEFAULT)
        self.entries.append(entry)
        log.info('Native minimap attached path=%s entries=%s', path, len(self.entries))

    def addPoint(self, symbol, position, number):
        matrix = Math.Matrix()
        matrix.setTranslate((position[0], 0.0, position[1]))
        entry = self.native.addEntry(symbol, 'points', matrix, True, TRANSFORM_FLAG.DEFAULT)
        self.entries.append(entry)
        self.native.entryInvoke(entry, ('setPointNumber', number))
        self.native.entryInvoke(entry, ('setState', 'default'))

    def _dispose(self):
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
        self.as_setMenuButtonsLabelsS('', u'Настройки', u'Вернуться к просмотру', u'Выйти в ангар')

    def _setMenuButtons(self):
        from gui.Scaleform.genConsts.INGAMEMENU_CONSTANTS import INGAMEMENU_CONSTANTS as buttons
        self.as_setMenuButtonsS([buttons.QUIT, buttons.SETTINGS, buttons.CANCEL])
