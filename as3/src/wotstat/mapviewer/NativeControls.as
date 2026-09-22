package wotstat.mapviewer {
  import flash.system.ApplicationDomain;
  import net.wg.infrastructure.events.LibraryLoaderEvent;

  // Shared stock controls; loading lobby.swf code into battle duplicates its
  // entire class bank and can exhaust the WoT Scaleform memory budget.
  public class NativeControls {
    private var ready:Function;
    private var failed:Function;
    private var disposed:Boolean = false;

    public function NativeControls(onReady:Function, onFailed:Function) {
      ready = onReady;
      failed = onFailed;
    }

    public function load():void {
      if (controlsReady()) { notifyReady(); return; }
      App.instance.loaderMgr.addEventListener(LibraryLoaderEvent.LOADED_COMPLETED, onControls);
      App.instance.loaderMgr.addEventListener(LibraryLoaderEvent.LOADING_FAILED, onControlsFailed);
      App.instance.loaderMgr.loadLibraries(new <String>['guiControlsLoginBattle.swf', 'guiControlsLobbyBattle.swf']);
    }

    private function onControls(event:LibraryLoaderEvent):void {
      if (!disposed && controlsReady()) notifyReady();
    }

    private function controlsReady():Boolean {
      for each (var symbol:String in ['ButtonNormal', 'CheckBox', 'Slider',
        'DropdownMenuUI', 'DropdownMenu_ScrollingList', 'DropDownListItemRendererSound', 'ScrollBar']) {
        if (!ApplicationDomain.currentDomain.hasDefinition(symbol)) return false;
      }
      return true;
    }

    private function notifyReady():void {
      removeListeners();
      if (disposed || ready == null) return;
      var callback:Function = ready;
      ready = null;
      try { callback(); } catch (error:Error) { failed(error.message); }
    }

    private function onControlsFailed(event:LibraryLoaderEvent):void {
      if (event.requestedUrl == 'guiControlsLoginBattle.swf' || event.requestedUrl == 'guiControlsLobbyBattle.swf') {
        removeListeners();
        if (!disposed && failed != null) failed('Native shared controls could not be loaded');
      }
    }

    private function removeListeners():void {
      App.instance.loaderMgr.removeEventListener(LibraryLoaderEvent.LOADED_COMPLETED, onControls);
      App.instance.loaderMgr.removeEventListener(LibraryLoaderEvent.LOADING_FAILED, onControlsFailed);
    }

    public function dispose():void {
      disposed = true;
      removeListeners();
      ready = failed = null;
    }
  }
}
