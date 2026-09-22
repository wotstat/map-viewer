# coding: utf-8
"""Temporary EU subhangar groups for the native hangar viewer."""
import logging

from . import debug_panel
from .localization import text

log = logging.getLogger('WOTSTAT_MAP_VIEWER')
SECTION = 'wotstat.map-viewer.hangar-scenes'

class HangarScenes(object):

  def __init__(self, spaceID, geometryName, lobbyApp):
    self.spaceID = spaceID
    self.geometryName = geometryName
    self.lobbyApp = lobbyApp
    self.scenes = {}
    self.selected = 'default'
    self._active = []
    self._environment = False
    self._registered = False

  def start(self):
    import Hangar
    import ResMgr
    from gui.subhangar.subhangar_observer import selectItemByTankSize

    # The current EU configuration defines these groups for the standard
    # hangar. Other hangars may have no matching prefab groups.
    if self.geometryName != 'hangar_v4' or not hasattr(Hangar, 'activateGroup'): return

    settings = ResMgr.openSection('spaces/subhangars.xml')
    if settings is None: return

    observer = getattr(self.lobbyApp, '_LobbyEntry__subhangarObserver', None)
    if observer is None or getattr(observer, '_SubhangarObserver__activatedSubHangars', None):
      return

    size = selectItemByTankSize((float('-inf'), 5.0, 8.0), ('Small', 'Medium', 'Large'))
    scenes = (
      ('default', ()),
      ('customization', ('CustomizationCommonGroup', 'CustomizationGroup')),
      ('overview', ('VehicleHubGroup', 'VehicleHubOverview%sTankGroup' % size)),
      ('armor', ('VehicleHubGroup', 'VehicleHubArmor%sTankGroup' % size)),
      ('victory', ('CustomizationCommonGroup', 'PostBattleCommonGroup',
             'PostBattle%sGroup' % size, 'PostBattleVictoryGroup')),
      ('defeat', ('CustomizationCommonGroup', 'PostBattleCommonGroup',
            'PostBattle%sGroup' % size, 'PostBattleDefeatGroup')),
      ('missions', ('PersonalMissionsGroup',)),
      ('pet', ('PetDenGroup',)),
    )
    available = set(name for name, _ in settings.items())
    self.scenes = dict((key, groups) for key, groups in scenes
              if all(group in available for group in groups))
    if len(self.scenes) < 2: return

    options = [dict(value=key, label=text('hangarScene_' + key))
          for key, _ in scenes if key in self.scenes]
    debug_panel.registerSection(SECTION, text('hangarScenes'), [dict(
      id='scene', type='dropdown', label=text('hangarScene'),
      value='default', options=options)], self.change)
    self._registered = True
    log.info('Hangar scenes ready: %s', ', '.join(self.scenes))

  def change(self, controlID, value):
    if controlID != 'scene' or value not in self.scenes:
      raise ValueError('Unknown hangar scene: %s' % value)
    if value == self.selected: return

    previous = self.selected
    try:
      self._clear()
      self._activate(value)
    except Exception:
      log.exception('Hangar scene switch failed: %s', value)
      self._clear()
      self._activate(previous)
      raise

    self.selected = value
    log.info('Hangar scene: %s', value)

  def _activate(self, value):
    import Hangar
    from helpers import dependency
    from skeletons.gui.shared.utils import IHangarSpace

    if value == 'customization':
      dependency.instance(IHangarSpace).space.getSpace().setEnvironment('Customization')
      self._environment = True

    for group in self.scenes[value]:
      Hangar.activateGroup(self.spaceID, group)
      self._active.append(group)

  def _clear(self):
    import Hangar
    from helpers import dependency
    from skeletons.gui.shared.utils import IHangarSpace

    changed = bool(self._active) or self._environment
    while self._active:
      group = self._active[-1]
      Hangar.deactivateGroup(self.spaceID, group)
      self._active.pop()

    if changed:
      dependency.instance(IHangarSpace).space.getSpace().resetEnvironment()
      self._environment = False

  def stop(self):
    if self._registered:
      debug_panel.unregisterSection(SECTION)
      self._registered = False

    self._clear()
    self.scenes = {}
