# coding: utf-8
MODE_ORDER = ('ctf', 'domination', 'assault', 'assault2', 'comp7', 'bob', 'maps_training')

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

def loadCatalog():
    import ArenaType
    import ResMgr
    from helpers import i18n
    from gui.Scaleform.daapi.view.lobby.trainings.formatters import getMapIconPath
    records = []
    for arenaID, arena in ArenaType.g_cache.iteritems():
        if ResMgr.openSection('spaces/' + arena.geometryName + '/space.settings') is None:
            continue
        label = i18n.makeString('#arenas:type/%s/name' % arena.gameplayName)
        label = displayName(label, arena.gameplayName)
        records.append(dict(key=arenaID, geometry=arena.geometryName,
                            name=displayName(arena.name, arena.geometryName),
                            mode=arena.gameplayName, modeLabel=label, size=arena.maxPlayersInTeam,
                            time=arena.roundLength / 60, description='', icon=getMapIconPath(arena)))
    return groupArenas(records)
