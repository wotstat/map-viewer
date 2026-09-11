def iterTeamPoints(bases, spawns, controls):
    # Battle atlas numbering follows arena_visitor, not the lobby atlas
    # frames or the base IDs stored in ArenaType.
    for team, points in enumerate(bases or (), 1):
        symbol = 'AllyTeamBaseEntry' if team == 1 else 'EnemyTeamBaseEntry'
        for index, point in enumerate(points.values(), 1):
            yield symbol, point, index if len(points) > 1 else 0
    for team, points in enumerate(spawns or (), 1):
        symbol = 'AllyTeamSpawnEntry' if team == 1 else 'EnemyTeamSpawnEntry'
        for index, point in enumerate(points, 1):
            yield symbol, point, index
    for index, point in enumerate(controls or (), 2):
        yield 'ControlPointEntry', point, index if len(controls) > 1 else 0
