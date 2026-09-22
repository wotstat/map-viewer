package wotstat.mapviewer {
  import flash.display.InteractiveObject;
  import flash.events.MouseEvent;

  public class DebugTooltip {
    private var target:InteractiveObject;
    private var text:String;
    private var shown:Boolean = false;

    public function DebugTooltip(view:InteractiveObject, value:String) {
      target = view;
      text = value;
      target.addEventListener(MouseEvent.ROLL_OVER, onOver);
      target.addEventListener(MouseEvent.ROLL_OUT, onOut);
      target.addEventListener(MouseEvent.MOUSE_DOWN, onOut);
    }

    private function onOver(event:MouseEvent):void {
      if (text) { App.toolTipMgr.show(text); shown = true; }
    }

    private function onOut(event:MouseEvent):void {
      hide();
    }

    public function setText(value:String):void {
      if (text == value) return;
      hide();
      text = value;
    }

    public function hide():void {
      if (shown) { App.toolTipMgr.hide(); shown = false; }
    }

    public function dispose():void {
      hide();
      target.removeEventListener(MouseEvent.ROLL_OVER, onOver);
      target.removeEventListener(MouseEvent.ROLL_OUT, onOut);
      target.removeEventListener(MouseEvent.MOUSE_DOWN, onOut);
      target = null;
      text = null;
    }
  }
}
