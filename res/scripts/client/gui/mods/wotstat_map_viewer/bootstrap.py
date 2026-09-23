# coding: utf-8
import logging
import BigWorld
import Keys
import game
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.shared.utils import IHangarSpace
from frameworks.wulf import WindowLayer
from gui.Scaleform.framework import g_entitiesFactories, ScopeTemplates, ViewSettings, ComponentSettings
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.Scaleform.framework.entities.View import View, ViewKey
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView
from .catalog import loadCatalog, modeLabel
from .localization import text, texts

log = logging.getLogger('WOTSTAT_MAP_VIEWER')
SELECTOR = 'wotstatMapViewerSelector'
BRIDGE = 'wotstatMapViewerBridge'
MENU = 'wotstatMapViewerMenu'
PREVIEW = 'wotstatMapViewerPreview'
MINIMAP = 'wotstatMapViewerMinimap'
HUD = 'wotstatMapViewerHUD'
bridge = None
selector = None
session = None
_installed = False
_keyOriginal = None
_mouseOriginal = None

def app():
  return dependency.instance(IAppLoader).getDefLobbyApp()

def findView(alias):
  target = session.battleApp if session and session.active and alias in (MENU, HUD, 'settingsWindow') else app()
  if target and target.containerManager:
    return target.containerManager.getViewByKey(ViewKey(alias))

def showSelector():
  if session and (session.active or session.restoring): return

  login = findView('login')
  if login is None or login.isDisposed():
    hangar = dependency.instance(IHangarSpace)
    if not hangar.spaceInited or BigWorld.player().__class__.__name__ != 'PlayerAccount':
      return

  if not bridge:
    app().loadView(SFViewLoadParams(BRIDGE))
  else:
    app().loadView(SFViewLoadParams(SELECTOR))

class Selector(AbstractWindowView):

  def __init__(self, ctx=None):
    super(Selector, self).__init__()
    self.rows = loadCatalog(includeHangars=findView('login') is None)
    self.selected = self.rows[0]['key'] if self.rows else None

  def _populate(self):
    global selector
    super(Selector, self)._populate()
    selector = self
    self.flashObject.as_setData(self.rows, texts())
    log.info('Own selector ready, maps=%d', len(self.rows))

  def modeSelected(self, arenaID):
    self.selected = arenaID

  def startViewing(self):
    arenaID = self.selected
    if arenaID is None: return

    self.destroy()
    BigWorld.callback(0.0, lambda: session.start(arenaID))

  def onWindowClose(self):
    self.destroy()

  def _dispose(self):
    global selector
    selector = None
    super(Selector, self)._dispose()

class Bridge(View):

  def ready(self):
    global bridge
    bridge = self
    log.info('UI bridge ready')
    app().loadView(SFViewLoadParams(SELECTOR))

  def loadingFailed(self):
    log.error('Could not load native minimap preview library')
    self.destroy()

  def _dispose(self):
    global bridge
    if session.active:
      session._abort()
    bridge = None
    super(Bridge, self)._dispose()

class BattleBridge(View):

  def __init__(self, ctx=None):
    super(BattleBridge, self).__init__()
    self._settingsSubscribed = False
    self._panelCallback = None

  def minimapReady(self, path):
    if session.active and not session.stopping and self.app == session.battleApp.proxy:
      try:
        session.hud = self
        self.getComponent(MINIMAP).attach(path, session.arena)

        from .debug_panel import g_registry
        from .catalog import displayName
        arena = session.arena
        mode = text('hangar') if session.isHangar else modeLabel(arena)

        labels = texts()
        if session._fromLogin:
          labels['toHangar'] = labels['toLogin']
        self.flashObject.as_setViewerData(
          displayName(arena.name, arena.geometryName), mode,
          g_registry.snapshot(), labels)
        self.flashObject.as_setVisibility(session.interfaceVisible, session.minimapVisible)
        g_registry.subscribe(self._settingsChanged)
        self._settingsSubscribed = True
        session._syncInputMode()
        session.notifyReady()
        if session._fromLogin:
          from gui.game_loading import loading
          loading.getLoader().idl()
        session._hideLoading()

        log.info('Local viewer ready; original minimap and camera attached')
      except Exception:
        log.exception('Native minimap initialization failed')
        BigWorld.callback(0.0, session.stop)

  def returnToHangar(self):
    if session.active and session.cursorControl and not session.stopping:
      BigWorld.callback(0.0, session.stop)

  def loadingFailed(self, message):
    log.error('Native viewer controls loading failed: %s', message)
    BigWorld.callback(0.0, session.stop)

  def settingChanged(self, sectionID, controlID, value, playing=None):
    if session.active and session.cursorControl and not session.stopping:
      from .debug_panel import g_registry
      if playing is not None:
        value = dict(position=value, playing=playing)
      g_registry.changeValue(sectionID, controlID, value)

  def inputLost(self):
    if session.active and not session.stopping:
      session.releaseInput()

  def _settingsChanged(self, kind, *args):
    if kind == 'sections':
      if self._panelCallback is None:
        self._panelCallback = BigWorld.callback(0.0, self._refreshSections)
    elif self._settingsSubscribed:
      self.flashObject.as_setControlValue(*args)

  def _refreshSections(self):
    from .debug_panel import g_registry
    self._panelCallback = None
    if self._settingsSubscribed:
      self.flashObject.as_setSections(g_registry.snapshot())

  def _dispose(self):
    from .debug_panel import g_registry

    g_registry.unsubscribe(self._settingsChanged)
    self._settingsSubscribed = False
    if self._panelCallback is not None:
      BigWorld.cancelCallback(self._panelCallback)
      self._panelCallback = None

    if session.hud is self:
      session.hud = None

    super(BattleBridge, self)._dispose()

def _handleKey(event):
  if session.active:
    return session.handleKey(event, _keyOriginal)
  if event.isKeyDown() and not event.isRepeatedEvent() and event.key == Keys.KEY_F8:
    showSelector()
    return True
  return _keyOriginal(event)

def _handleMouse(event):
  if session.active:
    return session.handleMouse(event)
  return _mouseOriginal(event)

def install():
  global _installed, _keyOriginal, _mouseOriginal, session
  if _installed: return

  from .viewer import LocalSession, LocalMinimap, LocalMenu
  from .preview import LocalPreview
  session = LocalSession()
  from .space_hooks import install as installSpaceHooks
  installSpaceHooks(session)

  for settings in (
    ViewSettings(
      SELECTOR, Selector, 'wotstatMapViewerSelector.swf',
      WindowLayer.WINDOW, None, ScopeTemplates.DEFAULT_SCOPE),
    ViewSettings(
      BRIDGE, Bridge, 'wotstatMapViewer.swf',
      WindowLayer.WINDOW, None, ScopeTemplates.GLOBAL_SCOPE,
      canDrag=False, canClose=False, isCentered=False),
    ComponentSettings(MINIMAP, LocalMinimap, ScopeTemplates.DEFAULT_SCOPE),
    ComponentSettings(PREVIEW, LocalPreview, ScopeTemplates.DEFAULT_SCOPE),
    ViewSettings(
      HUD, BattleBridge, 'wotstatMapViewerBattle.swf',
      WindowLayer.VIEW, None, ScopeTemplates.DEFAULT_SCOPE,
      canDrag=False, canClose=False, isCentered=False),
    ViewSettings(
      MENU, LocalMenu, 'ingameMenu.swf',
      WindowLayer.TOP_WINDOW, None, ScopeTemplates.DEFAULT_SCOPE,
      isModal=True, canClose=False, canDrag=False)):
    g_entitiesFactories.addSettings(settings)

  _keyOriginal, _mouseOriginal = game.handleKeyEvent, game.handleMouseEvent
  game.handleKeyEvent, game.handleMouseEvent = _handleKey, _handleMouse
  try:
    from gui.modsListApi import g_modsListApi
  except ImportError:
    log.info('ModsList unavailable; use F8')
  else:
    g_modsListApi.addModification(id='wotstat.map-viewer', name=text('title'),
                  description=text('description'),
                  icon='gui/maps/wotstat/map_viewer/modslist.png',
                  enabled=True, login=True, lobby=True, callback=showSelector)

  _installed = True
  log.info('Installed; open with F8 or ModsList')
