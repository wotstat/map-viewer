# coding: utf-8
import BigWorld
import Math
from account_helpers.settings_core import settings_constants as settings
from gui.battle_control.controllers.arena_border_ctrl import ArenaBorderController
from gui.shared.events import GameEvent


class LocalArenaBorder(ArenaBorderController):
    def attach(self, spaceID, boundingBox):
        self.startControl(None, None)
        # The stock loader reads Avatar.spaceID. Supply our local space while
        # retaining its settings, colours, fading and settings-change listener.
        self._ArenaBorderController__spaceID = spaceID
        bl, tr = boundingBox
        BigWorld.ArenaBorderHelper.setArenaBorderBounds(spaceID, Math.Vector4(bl.x, bl.y, tr.x, tr.y))
        self._applySetting(self.settingsCore.getSetting(settings.BATTLE_BORDER_MAP.MODE_SHOW_BORDER),
                           self.settingsCore.getSetting(settings.BATTLE_BORDER_MAP.TYPE_BORDER),
                           self._ArenaBorderController__getCurrentColor(self.settingsCore.getSetting(settings.GRAPHICS.COLOR_BLIND)))

    def extended(self, isDown):
        self._ArenaBorderController__handleShowExtendedInfo(GameEvent(GameEvent.SHOW_EXTENDED_INFO, {'isDown': isDown}))
