package wotstat.localmaps {
    import flash.display.Loader;
    import flash.events.Event;
    import flash.events.IOErrorEvent;
    import flash.system.ApplicationDomain;
    import flash.system.LoaderContext;
    import flash.utils.ByteArray;
    import net.wg.infrastructure.events.LibraryLoaderEvent;

    // Original lobby definitions are read from the installed client in memory.
    // The document binding is removed in Python before loading the class bank.
    public class NativeLobbyLibrary {
        private var library:Loader;
        private var ready:Function;
        private var failed:Function;
        private var disposed:Boolean = false;

        public function NativeLobbyLibrary(onReady:Function, onFailed:Function) {
            ready = onReady; failed = onFailed;
        }
        public function load(encoded:String):void {
            if (disposed) return;
            try {
                var bytes:ByteArray = decode(encoded);
                library = new Loader();
                library.contentLoaderInfo.addEventListener(Event.INIT, onLibrary);
                library.contentLoaderInfo.addEventListener(IOErrorEvent.IO_ERROR, onError);
                library.loadBytes(bytes, new LoaderContext(false, ApplicationDomain.currentDomain));
            } catch (error:Error) { fail(error.message); }
        }
        private function decode(encoded:String):ByteArray {
            var alphabet:String = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/';
            var table:Vector.<int> = new Vector.<int>(128, true);
            var i:int;
            for (i = 0; i < alphabet.length; ++i) table[alphabet.charCodeAt(i)] = i;
            var bytes:ByteArray = new ByteArray();
            for (i = 0; i < encoded.length; i += 4) {
                var a:int = table[encoded.charCodeAt(i)];
                var b:int = table[encoded.charCodeAt(i + 1)];
                var c:int = table[encoded.charCodeAt(i + 2)];
                var d:int = table[encoded.charCodeAt(i + 3)];
                bytes.writeByte((a << 2) | (b >> 4));
                if (encoded.charAt(i + 2) != '=') bytes.writeByte((b << 4) | (c >> 2));
                if (encoded.charAt(i + 3) != '=') bytes.writeByte((c << 6) | d);
            }
            bytes.position = 0; return bytes;
        }
        private function onLibrary(event:Event):void {
            if (disposed) return;
            if (ApplicationDomain.currentDomain.hasDefinition('BackButtonUI')) { notifyReady(); return; }
            App.instance.loaderMgr.addEventListener(LibraryLoaderEvent.LOADED_COMPLETED, onControls);
            App.instance.loaderMgr.addEventListener(LibraryLoaderEvent.LOADING_FAILED, onControlsFailed);
            App.instance.loaderMgr.loadLibraries(new <String>['guiControlsLobby.swf']);
        }
        private function onControls(event:LibraryLoaderEvent):void {
            if (!disposed && ApplicationDomain.currentDomain.hasDefinition('BackButtonUI')) {
                notifyReady();
            }
        }
        private function notifyReady():void {
            removeControlsListeners();
            if (ready == null) return;
            var callback:Function = ready; ready = null;
            try { callback(); } catch (error:Error) { fail(error.message); }
        }
        private function onControlsFailed(event:LibraryLoaderEvent):void {
            if (event.requestedUrl == 'guiControlsLobby.swf') fail('Native lobby controls could not be loaded');
        }
        private function onError(event:Event):void { fail(event.toString()); }
        private function fail(message:String):void {
            if (!disposed && failed != null) failed(message);
        }
        private function removeControlsListeners():void {
            App.instance.loaderMgr.removeEventListener(LibraryLoaderEvent.LOADED_COMPLETED, onControls);
            App.instance.loaderMgr.removeEventListener(LibraryLoaderEvent.LOADING_FAILED, onControlsFailed);
        }
        public function dispose():void {
            disposed = true; removeControlsListeners();
            if (library) {
                library.contentLoaderInfo.removeEventListener(Event.INIT, onLibrary);
                library.contentLoaderInfo.removeEventListener(IOErrorEvent.IO_ERROR, onError);
                library.unloadAndStop(true); library = null;
            }
            ready = failed = null;
        }
    }
}
