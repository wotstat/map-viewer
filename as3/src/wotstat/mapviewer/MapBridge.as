package wotstat.mapviewer {
  import flash.system.ApplicationDomain;
  import net.wg.infrastructure.base.AbstractView;
  import net.wg.infrastructure.events.LibraryLoaderEvent;

  // Keep the selector's stock controls available at both login and lobby.
  public class MapBridge extends AbstractView {
    public var ready:Function;
    public var loadingFailed:Function;
    private var notified:Boolean = false;
    private var controls:NativeControls;

    override protected function onPopulate():void {
      super.onPopulate();
      mouseEnabled = mouseChildren = false;
      controls = new NativeControls(onControlsReady, onControlsFailed);
      if (ApplicationDomain.currentDomain.hasDefinition('LobbyMinimap')) {
        loadControls();
      } else {
        App.instance.loaderMgr.addEventListener(LibraryLoaderEvent.LOADED_COMPLETED, onLibrariesLoaded);
        App.instance.loaderMgr.addEventListener(LibraryLoaderEvent.LOADING_FAILED, onLoadingFailed);
        App.instance.loaderMgr.loadLibraries(new <String>['MinimapLobby.swf']);
      }
    }

    private function onLibrariesLoaded(event:LibraryLoaderEvent):void {
      if (ApplicationDomain.currentDomain.hasDefinition('LobbyMinimap')) loadControls();
    }

    private function loadControls():void {
      removeLibraryListeners();
      controls.load();
    }

    private function onControlsReady():void {
      notifyReady();
    }

    private function onControlsFailed(message:String):void {
      loadingFailed();
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
      if (controls != null) controls.dispose();
      controls = null;
      ready = loadingFailed = null;
      super.onDispose();
    }
  }
}
