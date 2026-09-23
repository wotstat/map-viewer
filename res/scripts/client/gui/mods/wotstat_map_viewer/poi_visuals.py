# coding: utf-8
"""Static battle POI visuals in the viewer's local space."""
import logging

import BigWorld
import CGF
import GenericComponents
import Math
import ResMgr
from constants import AUTH_REALM

from .catalog import isWaffentragerArena

log = logging.getLogger('WOTSTAT_MAP_VIEWER')

# The battle entity supplies the radius over the network. The viewer has only
# ArenaType points, so use radii measured in EU and MT Onslaught replays.
ONSLAUGHT_RADII = {
  'EU': {1: 20.0, 2: 10.0},
  'RU': {1: 20.0, 2: 10.0, 3: 15.0, 4: 20.0},
}
# Other types have no matching local replay yet.
ONSLAUGHT_FALLBACK_RADIUS = 20.0
WT_GENERATOR = 'content/WtPrefabs/GeneratorModel.prefab'


def _onslaughtPrefab(radius):
  section = ResMgr.openSection('scripts/dynamic_objects.xml')
  section = section['pointOfInterest'] if section is not None else None
  if section is None:
    return None
  for _, prefab in section.items():
    bounds = prefab.readVector2('radiusRange')
    if bounds.x <= radius < bounds.y:
      return prefab.readString('path')
  return None


class PoiVisuals(object):

  def __init__(self, spaceID, arena):
    self.spaceID = spaceID
    self.arena = arena
    self._objects = []
    self._stopped = False

  def start(self):
    points = self.arena.pointsOfInterest or ()
    if not points:
      return
    onslaught = self.arena.gameplayName == 'comp7'
    if not onslaught and not isWaffentragerArena(self.arena):
      return

    for point in points:
      try:
        if onslaught:
          radius = ONSLAUGHT_RADII.get(AUTH_REALM, {}).get(
            point['type'], ONSLAUGHT_FALLBACK_RADIUS)
          prefab = _onslaughtPrefab(radius)
        else:
          radius = None
          prefab = WT_GENERATOR
        if not prefab:
          log.warning('POI prefab unavailable for %s', self.arena.geometryName)
          continue
        position = self._groundPosition(point['position'])
        self._load(prefab, position, radius)
      except Exception:
        log.exception('Could not create POI visual on %s', self.arena.geometryName)

  def _groundPosition(self, point):
    start = Math.Vector3(point.x, 1000.0, point.y)
    end = Math.Vector3(point.x, -1000.0, point.y)
    collide = (BigWorld.wg_collideSegment if AUTH_REALM == 'EU'
          else BigWorld.collideSegment)
    hit = collide(self.spaceID, start, end, 128)
    return Math.Vector3(hit.closestPoint) if hit is not None else Math.Vector3(point.x, 0.0, point.y)

  def _load(self, prefab, position, radius):
    if AUTH_REALM == 'EU':
      CGF.loadAndCreatePrefab(prefab, self.spaceID, position,
                lambda objects, queue: self._loadedEU(objects, queue, radius))
    else:
      transform = Math.Matrix()
      transform.setTranslate(position)
      CGF.loadGameObject(prefab, self.spaceID, transform,
                lambda gameObject: self._loadedMT(gameObject, radius))

  def _loadedEU(self, objects, queue, radius):
    if not objects:
      return
    root = objects[0]
    gameObject = queue.gameObject(root)
    if self._stopped:
      gameObject.destroy()
      return
    if radius is not None:
      area = queue.component(root, GenericComponents.TerrainSelectedAreaComponent)
      if area is not None:
        area.size = Math.Vector2(radius * 2, radius * 2)
      else:
        log.warning('POI prefab has no terrain selected area')
    self._objects.append(gameObject)
    queue.activateGameObject(root)

  def _loadedMT(self, gameObject, radius):
    if self._stopped:
      CGF.removeGameObject(gameObject)
      return
    if radius is not None:
      area = gameObject.findComponentByType(GenericComponents.TerrainSelectedAreaComponent)
      if area is not None:
        area.size = Math.Vector2(radius * 2, radius * 2)
      else:
        log.warning('POI prefab has no terrain selected area')
    self._objects.append(gameObject)
    gameObject.activate()

  def stop(self):
    self._stopped = True
    for gameObject in self._objects:
      try:
        if AUTH_REALM == 'EU':
          gameObject.destroy()
        else:
          CGF.removeGameObject(gameObject)
      except Exception:
        log.exception('Could not remove POI visual')
    self._objects = []
