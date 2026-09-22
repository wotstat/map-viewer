# coding: utf-8
import ArenaType
import Math
import ResMgr
from gui.Scaleform.daapi.view.lobby.MinimapLobby import MinimapLobby
from .minimap_bounds import getMinimapBounds

class LocalPreview(MinimapLobby):

  def setArena(self, arenaID):
    from .catalog import isHangarKey
    if isHangarKey(arenaID):
      return
    arena = ArenaType.g_cache[int(arenaID)]
    paths = ['gui/maps/icons/map/%s/%s.png' % (arena.gameplayName, arena.geometryName),
         'gui/maps/icons/map/%s.png' % arena.geometryName,
         arena.minimap]
    texture = next(('img://' + path for path in paths if path and ResMgr.isFile(path)),
            '')
    bounds = tuple(Math.Vector2(point) for point in getMinimapBounds(arena.boundingBox))
    self.setConfig(dict(texture=texture, size=bounds,
              teamBasePositions=arena.teamBasePositions or (),
              teamSpawnPoints=arena.teamSpawnPoints or (),
              controlPoints=arena.controlPoints or (),
              pointsOfInterest=arena.pointsOfInterest or ()))
