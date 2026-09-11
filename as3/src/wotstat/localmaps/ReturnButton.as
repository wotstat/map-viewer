package wotstat.localmaps {
    import flash.display.GradientType;
    import flash.display.MovieClip;
    import flash.display.Shape;
    import flash.filters.GlowFilter;
    import flash.geom.Matrix;
    import flash.text.TextField;
    import flash.text.TextFormat;
    import net.wg.gui.components.controls.SoundButton;

    // Stock button input/sound, with a small independent skin. The lobby-only
    // BackButton class and its class bank are not required by the battle movie.
    public class ReturnButton extends SoundButton {
        private var arrow:Shape;
        private var highlight:Shape;
        private var destination:TextField;
        private var interactive:Boolean = false;

        public function ReturnButton() {
            super();
            constraintsDisabled = true;
            preventAutosizing = true;
            highlight = new Shape();
            var matrix:Matrix = new Matrix();
            matrix.createGradientBox(90, 40, 0, 0, -6);
            highlight.graphics.beginGradientFill(GradientType.RADIAL,
                [0xFF4500, 0xA00000], [0.35, 0], [0, 255], matrix);
            highlight.graphics.drawRect(0, -6, 90, 40);
            highlight.graphics.endFill();
            addChild(highlight);

            arrow = new Shape();
            arrow.graphics.lineStyle(2, 0xFFDD99, 1, false, 'normal', 'none', 'miter');
            arrow.graphics.moveTo(16, 9);
            arrow.graphics.lineTo(12, 16);
            arrow.graphics.lineTo(16, 23);
            arrow.filters = [new GlowFilter(0xFF0000, 1, 10, 10, 1.5, 2)];
            addChild(arrow);

            // Same font, baseline, spacing and colours as the stock BackButton.
            textField = makeLabel('', 22, 0xFFDD99);
            textField.filters = [new GlowFilter(0xFF0000, 1, 10, 10, 1.5, 2)];
            destination = makeLabel('', 22 + textField.width + 3, 0xCCCCCC);
            destination.alpha = 0.8;
            hitMc = new MovieClip();
            addChild(hitMc);
            setLabels('', '');
            setState('up');
        }
        public function setLabels(back:String, target:String):void {
            label = back;
            textField.text = back;
            textField.width = Math.ceil(textField.textWidth) + 4;
            destination.text = target;
            destination.width = Math.ceil(destination.textWidth) + 4;
            destination.x = 22 + textField.width + 3;
            var hitWidth:Number = destination.x + destination.width + 10;
            hitMc.graphics.clear();
            hitMc.graphics.beginFill(0, 0);
            hitMc.graphics.drawRect(0, 0, hitWidth, 32);
            hitMc.graphics.endFill();
            setSize(hitWidth, 32);
        }
        private function makeLabel(value:String, left:Number, colour:uint):TextField {
            var field:TextField = App.textMgr.createTextField();
            var format:TextFormat = new TextFormat('$FieldFont', 12, colour);
            format.leading = 2;
            field.defaultTextFormat = format;
            field.embedFonts = true;
            field.selectable = field.mouseEnabled = false;
            field.text = value;
            field.x = left; field.y = 6;
            field.width = Math.ceil(field.textWidth) + 4;
            field.height = 20;
            addChild(field);
            return field;
        }
        public function setInteractive(value:Boolean):void {
            interactive = value;
            mouseEnabled = value;
            mouseChildren = false;
            if (!value) setState('up');
        }
        override protected function configUI():void {
            super.configUI();
            setInteractive(interactive);
        }
        override protected function setState(value:String):void {
            super.setState(value);
            if (highlight) highlight.visible = value == 'over' || value == 'release';
        }
        override protected function onDispose():void {
            arrow.filters = [];
            textField.filters = [];
            arrow = highlight = null;
            destination = null;
            super.onDispose();
        }
    }
}
