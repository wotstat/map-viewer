package wotstat.mapviewer {
  import flash.system.ApplicationDomain;
  import net.wg.infrastructure.base.AbstractView;
  import net.wg.infrastructure.events.LibraryLoaderEvent;

  // Persistent lobby lifecycle hook; no selector controls live here.
  public class MapBridge extends AbstractView {
    public var ready:Function;
    public var loadingFailed:Function;
    private var notified:Boolean = false;

    override protected function onPopulate():void {
      super.onPopulate();
      mouseEnabled = mouseChildren = false;
      if (ApplicationDomain.currentDomain.hasDefinition('LobbyMinimap')) {
        notifyReady();
      } else {
        App.instance.loaderMgr.addEventListener(LibraryLoaderEvent.LOADED_COMPLETED, onLibrariesLoaded);
        App.instance.loaderMgr.addEventListener(LibraryLoaderEvent.LOADING_FAILED, onLoadingFailed);
        App.instance.loaderMgr.loadLibraries(new <String>['MinimapLobby.swf']);
      }
    }

    private function onLibrariesLoaded(event:LibraryLoaderEvent):void {
      if (ApplicationDomain.currentDomain.hasDefinition('LobbyMinimap')) notifyReady();
    }

    private function onLoadingFailed(event:LibraryLoaderEvent):void {
      if (event.requestedUrl == 'MinimapLobby.swf' || event.url == 'MinimapLobby.swf') {
        removeLibraryListeners();
        loadingFailed();
      }
    }

    private function notifyReady():void {
      if (notified) return;
      notified = true;
      removeLibraryListeners();
      ready();
    }

    private function removeLibraryListeners():void {
      App.instance.loaderMgr.removeEventListener(LibraryLoaderEvent.LOADED_COMPLETED, onLibrariesLoaded);
      App.instance.loaderMgr.removeEventListener(LibraryLoaderEvent.LOADING_FAILED, onLoadingFailed);
    }

    override protected function onDispose():void {
      removeLibraryListeners();
      ready = loadingFailed = null;
      super.onDispose();
    }
  }
}
