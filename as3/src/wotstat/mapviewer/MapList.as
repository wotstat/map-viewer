package wotstat.mapviewer {
    import flash.text.TextField;
    import flash.text.TextFormat;
    import net.wg.gui.components.controls.DropDownListItemRendererSound;
    import scaleform.clik.controls.ScrollingList;

    public class MapList extends ScrollingList {
        public var eventsLabel:String = '';

        override protected function initialize():void {
            // CoreList needs authored bounds to rescale its renderer container.
            graphics.beginFill(0, 0); graphics.drawRect(0, 0, 1, 1); graphics.endFill();
            super.initialize();
        }

        override protected function populateData(items:Array):void {
            super.populateData(items);
            for (var i:int = 0; i < _renderers.length; ++i) {
                var renderer:DropDownListItemRendererSound = _renderers[i] as DropDownListItemRendererSound;
                if (!renderer) continue;
                // Restore the native text width when a renderer is reused after scrolling.
                renderer.invalidateSize();
                renderer.validateNow();
                var badge:TextField = renderer.getChildByName('wotstatEventsBadge') as TextField;
                if (i >= items.length || !items[i].dynamicEvents) {
                    if (badge) badge.visible = false;
                    continue;
                }
                if (!badge) {
                    badge = App.textMgr.createTextField();
                    badge.name = 'wotstatEventsBadge';
                    badge.defaultTextFormat = new TextFormat('$FieldFont', 10, 0xB5A77D, null, null, null, null, null, 'right');
                    badge.embedFonts = true; badge.selectable = badge.mouseEnabled = false;
                    renderer.addChild(badge);
                }
                badge.visible = true;
                badge.text = eventsLabel;
                badge.scaleX = badge.scaleY = 1;
                badge.width = badge.textWidth + 5; badge.height = 20;
                badge.scaleX = 1 / renderer.scaleX; badge.scaleY = 1 / renderer.scaleY;
                badge.x = renderer.textField.x + renderer.textField.width - badge.width - 6;
                badge.y = 3 / renderer.scaleY;
                renderer.textField.width = badge.x - renderer.textField.x - 4;
            }
        }
    }
}
