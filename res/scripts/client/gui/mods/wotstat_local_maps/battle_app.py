# coding: utf-8
"""The stock battle movie in a Flash root, without another Wulf MAIN_WINDOW.

RU 1.45 permits one MainWindow (it owns the shared window areas). Reusing the
game's initializer with a local factory keeps its DAAPI/managers intact and
does not patch application.MainWindow or switch the server GUI space.
"""
from types import FunctionType
from Event import Event
from gui import GUI_CTRL_MODE_FLAG
from constants import ARENA_GUI_TYPE
from gui.impl.gen import R
from gui.Scaleform.battle_entry import BattleEntry
from gui.Scaleform.framework.application import AppEntry, DAAPIRootBridge


class _FlashRoot(object):
    def __init__(self, owner):
        self.owner = owner
        self.onStatusChanged = Event()

    def load(self):
        self.owner.createComponent(swf='battle.swf')

    def destroy(self):
        self.onStatusChanged.clear()
        self.owner = None


class LocalBattleApp(BattleEntry):
    def __init__(self):
        self._arenaGuiType = ARENA_GUI_TYPE.RANDOM
        self._BattleEntry__input = None
        original = AppEntry.__init__.im_func
        localGlobals = dict(original.func_globals)
        localGlobals['MainWindow'] = lambda content: _FlashRoot(self)
        initialize = FunctionType(original.func_code, localGlobals,
                                  original.func_name, original.func_defaults,
                                  original.func_closure)
        initialize(self, R.entries.battle(), 'wotstat/localmaps',
                   GUI_CTRL_MODE_FLAG.CURSOR_ATTACHED,
                   DAAPIRootBridge(initCallback='registerBattleTest'))

    def afterCreate(self):
        # BattleGameInputMgr requires Avatar; all actual UI managers are stock.
        AppEntry.afterCreate(self)

    def _getRequiredLibraries(self):
        return super(LocalBattleApp, self)._getRequiredLibraries() + [
            'minimap.swf', 'minimapEntriesLibrary.swf']
