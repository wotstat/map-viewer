# coding: utf-8
"""Route native settings children/dialogs through the active local movie."""
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader


def _restore(handler, previous, local):
    # A real disconnect/app transition may already have installed a new target.
    if handler._app == local:
        handler.setApp(previous)


def routeCommonWindows(app, cleanup):
    factory = dependency.instance(IAppLoader)._AppLoader__appFactory
    importer = factory._AS3_AppFactory__importer
    for handler in importer._handlers['gui.Scaleform.daapi.view.common']:
        previous = handler._app
        cleanup.defer('restore native dialog routing', _restore, handler, previous, app.proxy)
        handler.setApp(app.proxy)
