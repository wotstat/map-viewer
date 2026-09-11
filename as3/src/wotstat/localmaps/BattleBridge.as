package wotstat.localmaps {
    import flash.display.DisplayObject;
    import flash.display.GradientType;
    import flash.display.Shape;
    import flash.events.Event;
    import flash.geom.Matrix;
    import flash.text.TextField;
    import flash.text.TextFormat;
    import net.wg.app.iml.base.StageResizeEvent;
    import net.wg.infrastructure.base.AbstractView;
    import net.wg.gui.battle.views.minimap.Minimap;
    import scaleform.clik.events.ButtonEvent;

    public class BattleBridge extends AbstractView {
        public var minimapReady:Function;
        public var returnToHangar:Function;
        public var settingChanged:Function;
        public var inputLost:Function;
        public var loadingFailed:Function;
        public var minimap:Minimap;
        public var backButton:ReturnButton;
        public var debugPanel:DebugPanel;
        private var nativeControls:NativeControls;
        private var header:Shape;
        private var title:TextField;
        private var mode:TextField;
        private var sizeIndex:int = 2;
        private var screenW:Number;
        private var screenH:Number;
        private var interfaceVisible:Boolean = true;
        private var hasSections:Boolean = false;

        override protected function onPopulate():void {
            super.onPopulate();
            mouseEnabled = false;
            App.stage.addEventListener(StageResizeEvent.STAGE_RESIZE, onStageResize);
            nativeControls = new NativeControls(buildControls, loadingFailed);
            nativeControls.load();
        }
        private function buildControls():void {
            header = new Shape(); addChild(header);
            backButton = new ReturnButton();
            backButton.name = 'backButton';
            backButton.x = 24; backButton.y = 28;
            addChild(backButton);
            backButton.validateNow();
            backButton.addEventListener(ButtonEvent.CLICK, onBack);
            title = makeLabel(20, 0xE9E2BF); title.y = 18;
            mode = makeLabel(13, 0xC9C9B6); mode.y = 46;
            debugPanel = new DebugPanel(); addChild(debugPanel);
            debugPanel.visible = false;
            debugPanel.changed = onSettingChanged;
            debugPanel.resized = positionPanel;
            debugPanel.beforeToggle = focusPanel;
            App.stage.addEventListener(Event.DEACTIVATE, onInputLost);
            minimap = App.utils.classFactory.getComponent('minimapUI', Minimap);
            minimap.name = 'minimap';
            addChild(minimap);
            registerFlashComponentS(minimap, 'wotstatLocalMapsMinimap');
            minimap.validateNow();
            minimap.setAllowedSizeIndex(sizeIndex);
            layoutMinimap();
            var names:Array=[];
            var d:DisplayObject=minimap.entriesContainer;
            while (d && d != App.stage) { names.unshift(d.name); d=d.parent; }
            names[0]='root'; // GFx exports the document root under this name.
            minimapReady('_level0.'+names.join('.'));
        }
        public function as_setViewerData(mapName:String, modeName:String, sections:Array, labels:Object):void {
            backButton.setLabels(labels.back, labels.toHangar);
            debugPanel.setLabels(labels.panelTitle, labels.mouseHint);
            title.text = mapName; mode.text = modeName;
            as_setSections(sections); layoutMinimap();
            as_setInteractive(false);
        }
        public function as_setSections(sections:Array):void {
            // AbstractView also remembers focus for the next modal activation.
            // Move it before disposing rows, including when another window is open.
            setFocus(this);
            debugPanel.setSections(sections);
            hasSections = sections.length > 0;
            debugPanel.visible = interfaceVisible && hasSections;
        }
        public function as_setControlValue(section:String, id:String, value:Object):void {
            debugPanel.setValue(section, id, value);
        }
        public function as_setInteractive(value:Boolean):void {
            backButton.setInteractive(value);
            debugPanel.setInteractive(value);
            if (!value) setFocus(this);
        }
        public function as_setVisibility(showInterface:Boolean, showMinimap:Boolean):void {
            interfaceVisible = showInterface;
            if (!showInterface) {
                setFocus(this);
                debugPanel.releaseInput();
            }
            header.visible = title.visible = mode.visible = showInterface;
            backButton.visible = showInterface;
            debugPanel.visible = showInterface && hasSections;
            minimap.visible = showInterface && showMinimap;
        }
        private function makeLabel(size:int, color:uint):TextField {
            var field:TextField = App.textMgr.createTextField();
            var format:TextFormat = new TextFormat('$FieldFont', size, color);
            format.align = 'center'; field.defaultTextFormat = format;
            field.embedFonts = true; field.selectable = false; field.mouseEnabled = false;
            field.height = 30; addChild(field); return field;
        }
        private function onBack(event:ButtonEvent):void { returnToHangar(); }
        private function focusPanel():void { setFocus(this); }
        private function onSettingChanged(section:String, id:String, value:Object):void {
            settingChanged(section, id, value);
        }
        private function onInputLost(event:Event):void { inputLost(); }
        private function onStageResize(event:StageResizeEvent):void {
            if (debugPanel) debugPanel.releaseInput();
            updateStage(Math.ceil(event.width / event.scale), Math.ceil(event.height / event.scale));
        }
        public function as_resizeMinimap(delta:int):void {
            sizeIndex = Math.max(0, Math.min(5, sizeIndex + delta));
            minimap.setAllowedSizeIndex(sizeIndex);
            minimap.validateNow();
            layoutMinimap();
        }
        override public function updateStage(w:Number,h:Number):void {
            super.updateStage(w,h);
            screenW=w; screenH=h; layoutMinimap();
        }
        private function layoutMinimap():void {
            var w:Number = screenW || App.appWidth;
            var h:Number = screenH || App.appHeight;
            if (minimap) {
                minimap.x = w-minimap.currentWidth;
                minimap.y = h-minimap.currentHeight;
            }
            if (header) {
                var matrix:Matrix = new Matrix(); matrix.createGradientBox(w, 96, Math.PI / 2);
                header.graphics.clear();
                header.graphics.beginGradientFill(GradientType.LINEAR, [0x080A08,0x080A08], [0.72,0], [0,255], matrix);
                header.graphics.drawRect(0,0,w,96); header.graphics.endFill();
                title.x = mode.x = Math.max(260, (w - 440) / 2);
                title.width = mode.width = Math.min(440, Math.max(150, w - title.x - 24));
            }
            if (debugPanel) {
                debugPanel.setMaxHeight(Math.min(440, h-150));
                positionPanel();
            }
        }
        private function positionPanel():void {
            if (debugPanel) { debugPanel.x=20; debugPanel.y=(screenH || App.appHeight)-20-debugPanel.panelHeight; }
        }
        override protected function onDispose():void {
            App.stage.removeEventListener(Event.DEACTIVATE, onInputLost);
            App.stage.removeEventListener(StageResizeEvent.STAGE_RESIZE, onStageResize);
            if (debugPanel) { debugPanel.dispose(); debugPanel = null; }
            if (backButton) {
                backButton.removeEventListener(ButtonEvent.CLICK, onBack);
                backButton.dispose(); backButton = null;
            }
            if (minimap) {
                removeChild(minimap);
                minimap=null;
            }
            minimapReady=null;
            returnToHangar = settingChanged = inputLost = null;
            loadingFailed = null;
            if (nativeControls) { nativeControls.dispose(); nativeControls = null; }
            header = null; title = mode = null;
            super.onDispose();
        }
    }
}
