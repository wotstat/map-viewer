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
                var badge:TextField = renderer.getChildByName('wotstatEventsBadge') as TextField;
                if (!badge) {
                    badge = App.textMgr.createTextField();
                    badge.name = 'wotstatEventsBadge';
                    badge.defaultTextFormat = new TextFormat('$FieldFont', 10, 0xB5A77D, null, null, null, null, null, 'right');
                    badge.embedFonts = true; badge.selectable = badge.mouseEnabled = false;
                    renderer.addChild(badge);
                }
                badge.text = i < items.length && items[i].dynamicEvents ? eventsLabel : '';
                badge.scaleX = badge.scaleY = 1;
                badge.width = badge.textWidth + 5; badge.height = 20;
                var badgeWidth:Number = badge.width;
                badge.scaleX = 1 / renderer.scaleX; badge.scaleY = 1 / renderer.scaleY;
                badge.x = (renderer.width - badgeWidth - 6) / renderer.scaleX;
                badge.y = 3 / renderer.scaleY;
                renderer.textField.width = (badge.text ? badge.x - 4 / renderer.scaleX :
                    (renderer.width - 6) / renderer.scaleX) - renderer.textField.x;
            }
        }
    }
}
