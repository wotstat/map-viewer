package wotstat.localmaps {
    import flash.text.TextField;
    import flash.text.TextFormat;
    import net.wg.infrastructure.base.AbstractWindowView;
    import net.wg.gui.components.controls.DropdownMenu;
    import scaleform.clik.controls.ScrollingList;
    import net.wg.gui.components.controls.SoundButtonEx;
    import net.wg.gui.components.minimap.MinimapPresentation;
    import scaleform.clik.data.DataProvider;
    import scaleform.clik.events.ButtonEvent;
    import scaleform.clik.events.ListEvent;

    public class MapSelector extends AbstractWindowView {
        public var modeSelected:Function;
        public var startViewing:Function;
        public var maps:ScrollingList;
        public var modes:DropdownMenu;
        public var minimap:MinimapPresentation;
        public var mapName:TextField;
        public var startButton:SoundButtonEx;
        public var closeButton:SoundButtonEx;
        private var rows:Array = [];
        private var mapLabel:TextField;
        private static const CONTENT_W:int = 640;
        private static const CONTENT_H:int = 442;
        private static const PREVIEW_SIZE:int = 340;
        private static const NATIVE_PREVIEW_SIZE:int = 300;

        public function MapSelector() {
            super();
            setSize(CONTENT_W, CONTENT_H);
        }
        override protected function onPopulate():void {
            // No authored room layout or deferred rearrangement.
            super.onPopulate();
            window.title = 'Локальный просмотр карт';
            window.useBottomBtns = true;
            mapLabel = makeLabel('Выбор карты:', 8, 4, 250, 14);
            mapName = makeLabel('', 286, 0, PREVIEW_SIZE, 20);
            maps = App.utils.classFactory.getComponent('ScrollingList', ScrollingList);
            maps.name = 'maps';
            maps.x = 8; maps.y = 30;
            maps.setSize(258, 374);
            maps.itemRendererName = 'DropDownListItemRendererSound';
            maps.scrollBar = 'ScrollBar';
            maps.rowHeight = 22;
            addChild(maps);
            modes = App.utils.classFactory.getComponent('DropdownMenuUI', DropdownMenu);
            modes.name = 'modes';
            modes.x = 286; modes.y = 30; modes.width = PREVIEW_SIZE;
            modes.dropdown = 'DropdownMenu_ScrollingList';
            modes.itemRenderer = 'DropDownListItemRendererSound';
            modes.menuRowsFixed = false; modes.rowCount = -1;
            addChild(modes);
            minimap = App.utils.classFactory.getComponent('LobbyMinimap', MinimapPresentation);
            minimap.name = 'minimap';
            minimap.x = 286; minimap.y = 64;
            minimap.scaleX = minimap.scaleY = PREVIEW_SIZE / NATIVE_PREVIEW_SIZE;
            minimap.scope = 'createRoom';
            addChild(minimap);
            startButton = makeButton('Начать просмотр', 332, 180);
            closeButton = makeButton('Закрыть', 522, 104);
            startButton.enabled = false;
            maps.addEventListener(ListEvent.INDEX_CHANGE, onMapChanged);
            modes.addEventListener(ListEvent.INDEX_CHANGE, onModeChanged);
            startButton.addEventListener(ButtonEvent.CLICK, onStart);
            closeButton.addEventListener(ButtonEvent.CLICK, onClose);
            registerFlashComponentS(minimap, 'wotstatLocalMapsPreview');
        }
        public function as_setData(data:Array):void {
            rows = data;
            maps.dataProvider = new DataProvider(rows);
            maps.selectedIndex = rows.length ? 0 : -1;
            maps.validateNow();
            onMapChanged(null);
            // AbstractView normally reveals its contents on the next frame.
            // The controls are ready now, so show them with the native frame.
            visible = true;
        }
        private function makeLabel(text:String, left:int, top:int, w:int, size:int):TextField {
            var field:TextField = App.textMgr.createTextField();
            field.defaultTextFormat = new TextFormat('$FieldFont', size, 0xC9C9B6);
            field.embedFonts = true; field.selectable = false; field.mouseEnabled = false;
            field.x = left; field.y = top; field.width = w; field.height = 28;
            field.text = text;
            addChild(field);
            return field;
        }
        private function makeButton(label:String, left:int, w:int):SoundButtonEx {
            var button:SoundButtonEx = App.utils.classFactory.getComponent('ButtonNormal', SoundButtonEx);
            button.label = label; button.width = w;
            button.x = left; button.y = CONTENT_H - 22;
            addChild(button);
            return button;
        }
        private function onMapChanged(event:ListEvent):void {
            if (maps.selectedIndex < 0 || maps.selectedIndex >= rows.length) return;
            var row:Object = rows[maps.selectedIndex];
            mapName.text = row.name;
            modes.dataProvider = new DataProvider(row.modes);
            modes.selectedIndex = row.modes.length ? 0 : -1;
            modes.validateNow();
            onModeChanged(null);
        }
        private function onModeChanged(event:ListEvent):void {
            startButton.enabled = modes.selectedIndex >= 0;
            if (!startButton.enabled) return;
            var id:Number = modes.dataProvider[modes.selectedIndex].key;
            minimap.setMinimapDataS(id, 1, NATIVE_PREVIEW_SIZE);
            modeSelected(id);
        }
        private function onStart(event:ButtonEvent):void { startViewing(); }
        private function onClose(event:ButtonEvent):void { onWindowCloseS(); }
        override protected function onBeforeDispose():void {
            maps.removeEventListener(ListEvent.INDEX_CHANGE, onMapChanged);
            modes.removeEventListener(ListEvent.INDEX_CHANGE, onModeChanged);
            startButton.removeEventListener(ButtonEvent.CLICK, onStart);
            closeButton.removeEventListener(ButtonEvent.CLICK, onClose);
            super.onBeforeDispose();
        }
        override protected function onDispose():void {
            maps.dispose(); maps = null;
            modes.dispose(); modes = null;
            startButton.dispose(); startButton = null;
            closeButton.dispose(); closeButton = null;
            minimap = null; mapName = mapLabel = null; rows = null;
            modeSelected = startViewing = null;
            super.onDispose();
        }
    }
}
