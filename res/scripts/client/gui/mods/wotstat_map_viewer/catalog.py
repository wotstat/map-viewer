# coding: utf-8
MODE_ORDER = ('ctf', 'domination', 'assault', 'assault2', 'comp7', 'bob', 'maps_training')
HANGAR_PREFIX = 'hangar:'

def displayName(value, fallback):
  if not value or value.startswith(('#', 'type/')):
    return fallback
  return value

def groupArenas(records):
  groups = {}
  for record in records:
    groups.setdefault(record['geometry'], []).append(dict(record))

  rows = []
  for modes in groups.values():
    modes.sort(key=lambda r: (MODE_ORDER.index(r['mode']) if r['mode'] in MODE_ORDER else 100, r['key']))
    row = dict(modes[0])
    row['label'] = row['name']
    row['arenaType'] = row['modeLabel']
    row['modes'] = [dict(key=m['key'], label=m['modeLabel']) for m in modes]
    rows.append(row)

  return sorted(rows, key=lambda r: (r['name'].lower(), r['geometry']))

def hangarKey(name):
  return HANGAR_PREFIX + name

def isHangarKey(key):
  return isinstance(key, basestring) and key.startswith(HANGAR_PREFIX)

def loadHangars():
  import ResMgr
  from .localization import text

  spaces = ResMgr.openSection('spaces')
  if spaces is None: return []

  rows = []
  label = text('hangar')
  for name, _ in spaces.items():
    if ResMgr.openSection('spaces/' + name + '/space.settings/hangarSettings') is None: continue

    key = hangarKey(name)
    title = u'%s: %s' % (label, name)
    rows.append(dict(key=key, geometry=name, name=title, label=title,
             arenaType=label, modes=[dict(key=key, label=label)],
             kind='hangar', dynamicEvents=False, size=0, time=0,
             description='', icon=''))

  return sorted(rows, key=lambda row: row['geometry'])

class HangarArena(object):

  def __init__(self, name):
    import Math
    import ResMgr
    from .localization import text

    settings = ResMgr.openSection('spaces/' + name + '/space.settings')
    if settings is None or settings['hangarSettings'] is None:
      raise ValueError('Hangar space is unavailable: %s' % name)

    bounds = settings['bounds']
    chunk = settings.readFloat('chunkSize', 100.0)
    self.boundingBox = (Math.Vector2(bounds.readInt('minX') * chunk,
                     bounds.readInt('minY') * chunk),
              Math.Vector2((bounds.readInt('maxX') + 1) * chunk,
                     (bounds.readInt('maxY') + 1) * chunk))

    start = settings['hangarSettings'].readVector3('v_start_pos')
    self.startPosition = (start.x, start.y + 20.0, start.z - 40.0)
    self.geometryName = name
    self.gameplayName = 'hangar'
    self.gameplayID = None
    self.name = u'%s: %s' % (text('hangar'), name)
    self.minimap = ''
    self.teamBasePositions = ()
    self.teamSpawnPoints = ()
    self.controlPoints = ()
    self.pointsOfInterest = ()
    self.minimapLayers = {}

def loadCatalog():
  import ArenaType
  import ResMgr
  from constants import AUTH_REALM
  from helpers import i18n

  records = []
  for arenaID, arena in ArenaType.g_cache.iteritems():
    if ResMgr.openSection('spaces/' + arena.geometryName + '/space.settings') is None: continue

    label = i18n.makeString('#arenas:type/%s/name' % arena.gameplayName)
    label = displayName(label, arena.gameplayName)
    records.append(dict(key=arenaID, geometry=arena.geometryName,
              dynamicEvents=(AUTH_REALM == 'EU' and
                      not arena.geometryName.endswith(('_sm24', '_sm25')) and
                      bool(getattr(arena, 'minimapLayers', None))),
              name=displayName(arena.name, arena.geometryName),
              mode=arena.gameplayName, modeLabel=label, size=arena.maxPlayersInTeam,
              time=arena.roundLength / 60, description='',
              icon='../maps/icons/map/%s.png' % arena.geometryName))

  return groupArenas(records) + loadHangars()
