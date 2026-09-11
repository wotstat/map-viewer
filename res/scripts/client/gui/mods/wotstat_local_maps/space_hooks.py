# coding: utf-8
"""Keep stock sound-zone construction in the client-only space.

The stock UDO constructor assumes player().spaceID is a battle world. Account
has spaceID=0. Only that constructor receives a CGF facade; the global CGF and
BigWorld modules, the player and all other game object constructors are intact.
"""
from types import FunctionType
import CGF
import BigWorld


def install(session):
    # This UDO exists only in MT. WoT has no corresponding constructor to fix.
    import ResMgr
    if not ResMgr.isFile('scripts/client/SoundZoneTrigger.pyc'):
        return
    import SoundZoneTrigger
    original = SoundZoneTrigger.SoundZoneTrigger.__init__

    class ZoneCGF(object):
        def __getattr__(self, name):
            return getattr(CGF, name)

        def GameObject(self, spaceID, *args):
            if session.active and spaceID == 0 and session.spaceID is not None:
                spaceID = session.spaceID
            return CGF.GameObject(spaceID, *args)

    function = original.im_func
    localGlobals = dict(function.func_globals, CGF=ZoneCGF())
    scoped = FunctionType(function.func_code, localGlobals, function.func_name,
                          function.func_defaults, function.func_closure)

    def initialize(zone):
        if session.active and session.spaceID is not None:
            return scoped(zone)
        return original(zone)

    SoundZoneTrigger.SoundZoneTrigger.__init__ = initialize
