# coding: utf-8
import BigWorld
from gui.Scaleform.daapi.view.common.waiting_transitions import WaitingTransition, TransitionMode
from gui.impl.gen import R
from account_helpers.settings_core import settings_constants


class LoadingCover(WaitingTransition):
    """An independent stock loading movie surviving both world lifecycles."""
    def __init__(self, action):
        self._action = action
        self._callback = None
        try:
            super(LoadingCover, self).__init__()
            self.component.position.z = 0.0
            self.setTransitionMode(TransitionMode.ENABLED)
            self.showWaiting(R.strings.waiting.loading())
        except Exception:
            self.close()
            raise

    def afterCreate(self):
        super(LoadingCover, self).afterCreate()
        self.movie.backgroundAlpha = 1.0
        self.settingsCore.options.getSetting(settings_constants.GRAPHICS.INTERFACE_SCALE).updateScale()
        # Allow the initialized movie to reach the screen before blocking IO.
        self._callback = BigWorld.callback(0.15, self._run)

    def _run(self):
        self._callback = None
        action, self._action = self._action, None
        if action:
            action()

    def close(self):
        if self._callback is not None:
            BigWorld.cancelCallback(self._callback)
            self._callback = None
        self._action = None
        super(LoadingCover, self).close()
