package wotstat.localmaps {
    import flash.display.Sprite;
    import flash.events.Event;
    import flash.events.MouseEvent;
    import flash.geom.Rectangle;
    import flash.text.TextField;
    import flash.text.TextFormat;
    import net.wg.gui.components.controls.ScrollBar;
    import net.wg.gui.components.controls.SoundButtonEx;
    import scaleform.clik.events.ButtonEvent;

    public class DebugPanel extends Sprite {
        public var changed:Function;
        public var resized:Function;
        public var panelHeight:int = 70;
        public static const PANEL_W:int = 312;
        public var scrollBar:ScrollBar;
        private var viewport:Sprite = new Sprite();
        private var body:Sprite = new Sprite();
        private var sections:Array = [];
        private var controls:Array = [];
        private var headers:Array = [];
        private var collapsed:Object = {};
        private var maxHeight:int = 440;
        private var contentHeight:int = 0;
        private var viewHeight:int = 0;
        private var interactive:Boolean = false;

        public function DebugPanel() {
            super();
            name = 'debugPanel';
            makeLabel(this, 'ПАРАМЕТРЫ ПРОСМОТРА', 14, 10, 17);
            makeLabel(this, 'Ctrl — управление мышью', 14, 33, 12, 0x8F8F80);
            viewport.x = 14; viewport.y = 60;
            viewport.addChild(body); addChild(viewport);
            scrollBar = App.utils.classFactory.getComponent('ScrollBar', ScrollBar);
            scrollBar.name = 'scrollBar'; scrollBar.x = PANEL_W - 21; scrollBar.y = 60;
            addChild(scrollBar);
            scrollBar.addEventListener(Event.SCROLL, onScroll);
            addEventListener(MouseEvent.MOUSE_WHEEL, onWheel);
            setInteractive(false);
        }
        public function setSections(data:Array):void {
            releaseInput();
            clearRows(); sections = data;
            var retained:Object = {};
            for each (var section:Object in sections) {
                retained[section.id] = collapsed[section.id] === true;
                var header:Sprite = new Sprite();
                header.name = 'section_' + section.id;
                header.graphics.beginFill(0xFFFFFF, 0.035);
                header.graphics.drawRect(-6, 0, PANEL_W - 34, 28); header.graphics.endFill();
                makeLabel(header, section.title, 0, 3, 15, 0xE9E2BF);
                var toggle:SoundButtonEx = App.utils.classFactory.getComponent('ButtonBlack', SoundButtonEx);
                toggle.name = section.id; toggle.x = PANEL_W - 66; toggle.y = 3; toggle.width = 24;
                toggle.addEventListener(ButtonEvent.CLICK, onToggle);
                header.addChild(toggle); body.addChild(header);
                headers.push({id:section.id, view:header, toggle:toggle});
                for each (var dataControl:Object in section.controls) {
                    var control:DebugControl = new DebugControl(section.id, dataControl, PANEL_W - 52, onChanged);
                    body.addChild(control); controls.push(control);
                }
            }
            collapsed = retained;
            scrollBar.position = 0;
            layout();
        }
        public function setValue(section:String, id:String, value:Object):void {
            for each (var control:DebugControl in controls) {
                if (control.sectionID == section && control.controlID == id) {
                    control.setValue(value); return;
                }
            }
        }
        public function setMaxHeight(value:int):void {
            maxHeight = Math.max(120, value); layout();
        }
        private function layout():void {
            var top:int = 0;
            for each (var header:Object in headers) {
                header.view.y = top; top += 36;
                header.toggle.label = collapsed[header.id] ? '+' : '-';
                for each (var control:DebugControl in controls) {
                    if (control.sectionID != header.id) continue;
                    control.visible = !collapsed[header.id];
                    if (control.visible) { control.y = top; top += control.rowHeight; }
                }
                top += 6;
            }
            contentHeight = top;
            viewHeight = Math.max(1, Math.min(contentHeight, maxHeight - 72));
            panelHeight = viewHeight + 72;
            viewport.scrollRect = new Rectangle(0, 0, PANEL_W - 40, viewHeight);
            scrollBar.height = viewHeight;
            scrollBar.setScrollProperties(viewHeight, 0, Math.max(0, contentHeight - viewHeight), 28);
            scrollBar.position = Math.min(scrollBar.position, Math.max(0, contentHeight - viewHeight));
            scrollBar.visible = contentHeight > viewHeight;
            scrollBar.validateNow(); onScroll(null);
            graphics.clear();
            graphics.lineStyle(1, 0xAEA58B, 0.23);
            graphics.beginFill(0x10110E, 0.80);
            graphics.drawRoundRect(0, 0, PANEL_W, panelHeight, 3); graphics.endFill();
            graphics.lineStyle(1, 0xAEA58B, 0.16);
            graphics.moveTo(14, 53); graphics.lineTo(PANEL_W - 14, 53);
            if (resized != null) resized();
        }
        private function makeLabel(parent:Sprite, text:String, left:int, top:int, size:int,
                                   color:uint = 0xE9E2BF):TextField {
            var field:TextField = App.textMgr.createTextField();
            field.defaultTextFormat = new TextFormat('$FieldFont', size, color);
            field.embedFonts = true; field.selectable = false; field.mouseEnabled = false;
            field.x = left; field.y = top; field.width = PANEL_W - 72; field.height = 25;
            field.text = text; parent.addChild(field); return field;
        }
        private function onChanged(section:String, id:String, value:Object):void {
            if (interactive && changed != null) changed(section, id, value);
        }
        private function onToggle(event:ButtonEvent):void {
            var id:String = SoundButtonEx(event.currentTarget).name;
            releaseInput(); collapsed[id] = !collapsed[id]; layout();
        }
        private function onScroll(event:Event):void {
            body.y = -Math.round(scrollBar.position);
        }
        private function onWheel(event:MouseEvent):void {
            if (!interactive || !scrollBar.visible) return;
            releaseInput(); scrollBar.position -= event.delta * 24;
            event.stopPropagation();
        }
        public function setInteractive(value:Boolean):void {
            if (interactive && !value) releaseInput();
            interactive = value;
            mouseEnabled = mouseChildren = value;
            alpha = value ? 1.0 : 0.84;
        }
        public function releaseInput():void {
            for each (var control:DebugControl in controls) control.releaseInput();
            // Native sliders and scrollbars terminate their stage drag here.
            if (interactive && stage) stage.dispatchEvent(new MouseEvent(MouseEvent.MOUSE_UP));
        }
        private function clearRows():void {
            for each (var control:DebugControl in controls) control.dispose();
            for each (var header:Object in headers) {
                header.toggle.removeEventListener(ButtonEvent.CLICK, onToggle);
                header.toggle.dispose();
            }
            while (body.numChildren) body.removeChildAt(0);
            controls = []; headers = [];
        }
        public function dispose():void {
            releaseInput(); clearRows();
            removeEventListener(MouseEvent.MOUSE_WHEEL, onWheel);
            scrollBar.removeEventListener(Event.SCROLL, onScroll);
            scrollBar.dispose(); scrollBar = null;
            changed = resized = null; sections = null; collapsed = null;
        }
    }
}
