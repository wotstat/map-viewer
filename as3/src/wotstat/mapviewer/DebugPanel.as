package wotstat.mapviewer {
  import flash.display.Sprite;
  import flash.events.Event;
  import flash.events.MouseEvent;
  import flash.geom.Rectangle;
  import flash.text.TextField;
  import flash.text.TextFormat;
  import net.wg.gui.components.controls.ScrollBar;

  public class DebugPanel extends Sprite {
    public var changed:Function;
    public var resized:Function;
    public var beforeToggle:Function;
    public var panelHeight:int = 70;
    public static const PANEL_W:int = 312;
    private static const PANEL_INSET:int = 16;
    private static const GROUP_W:int = PANEL_W - PANEL_INSET * 2;
    private static const SCROLLBAR_GUTTER:int = 24;
    private static const CONTENT_INSET:int = 20;
    private static const HEADER_H:int = 32;
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
    private var panelTitle:TextField;
    private var mouseHint:TextField;

    public function DebugPanel() {
      super();
      name = 'debugPanel';
      panelTitle = makeLabel(this, '', 14, 10, 17);
      mouseHint = makeLabel(this, '', 14, 33, 12, 0x8F8F80);
      panelTitle.width = mouseHint.width = PANEL_W - 28;
      viewport.x = PANEL_INSET;
      viewport.y = 60;
      viewport.addChild(body);
      addChild(viewport);
      scrollBar = App.utils.classFactory.getComponent('ScrollBar', ScrollBar);
      scrollBar.name = 'scrollBar';
      scrollBar.x = PANEL_W - 21;
      scrollBar.y = 60;
      addChild(scrollBar);
      scrollBar.addEventListener(Event.SCROLL, onScroll);
      addEventListener(MouseEvent.MOUSE_WHEEL, onWheel);
      setInteractive(false);
    }

    public function setLabels(title:String, hint:String):void {
      panelTitle.text = title;
      mouseHint.text = hint;
      var format:TextFormat = panelTitle.defaultTextFormat;
      format.size = 17;
      panelTitle.setTextFormat(format);
      while (panelTitle.textWidth > panelTitle.width - 4 && Number(format.size) > 12) {
        format.size = Number(format.size) - 1;
        panelTitle.setTextFormat(format);
      }
    }

    public function setSections(data:Array):void {
      releaseInput();
      clearRows();
      sections = data;
      var retained:Object = {};
      for each (var section:Object in sections) {
        retained[section.id] = collapsed.hasOwnProperty(section.id) ? collapsed[section.id] : true;
        var header:Sprite = new Sprite();
        header.name = 'section_' + section.id;
        var title:TextField = makeLabel(header, section.title, 24, 4, 16);
        title.defaultTextFormat = new TextFormat('$TitleFont', 16, 0xE9E2BF);
        title.setTextFormat(title.defaultTextFormat);
        title.height = HEADER_H - 4;
        var arrow:Sprite = new Sprite();
        arrow.name = 'arrow';
        arrow.x = 8;
        arrow.y = HEADER_H / 2;
        arrow.mouseEnabled = false;
        arrow.graphics.lineStyle(2, 0xE9E2BF);
        arrow.graphics.moveTo(-2, -4);
        arrow.graphics.lineTo(2, 0);
        arrow.graphics.lineTo(-2, 4);
        header.addChild(arrow);
        // The entire title strip toggles the section and owns its tooltip.
        var titleHit:Sprite = new Sprite();
        titleHit.name = section.id;
        titleHit.buttonMode = true;
        titleHit.addEventListener(MouseEvent.CLICK, onToggle);
        titleHit.addEventListener(MouseEvent.ROLL_OVER, onHeaderOver);
        titleHit.addEventListener(MouseEvent.ROLL_OUT, onHeaderOut);
        header.addChild(titleHit);
        body.addChild(header);
        headers.push({id:section.id, view:header, label:title, arrow:arrow,
          title:section.title, help:section.tooltip, titleHit:titleHit,
          tooltip:new DebugTooltip(titleHit, section.tooltip || '')});
        for each (var dataControl:Object in section.controls) {
          var control:DebugControl = new DebugControl(section.id, dataControl,
            GROUP_W - CONTENT_INSET * 2, onChanged);
          control.x = CONTENT_INSET;
          body.addChild(control);
          controls.push(control);
        }
      }
      collapsed = retained;
      scrollBar.position = 0;
      layout();
    }

    public function setValue(section:String, id:String, value:Object):void {
      for each (var control:DebugControl in controls) {
        if (control.sectionID == section && control.controlID == id) {
          control.setValue(value);
          return;
        }
      }
    }

    public function setMaxHeight(value:int):void {
      maxHeight = Math.max(120, value);
      layout();
    }

    private function layout():void {
      // Measure at full width first, so removing overflow restores the
      // symmetric margins. Narrow text may wrap and increase row heights.
      var groupWidth:int = GROUP_W;
      contentHeight = layoutGroups(groupWidth);
      var available:int = maxHeight - 66;
      var needsScroll:Boolean = contentHeight > available;
      if (needsScroll) {
        groupWidth -= SCROLLBAR_GUTTER;
        contentHeight = layoutGroups(groupWidth);
      }
      viewHeight = Math.max(1, Math.min(contentHeight, available));
      panelHeight = viewHeight + 66;
      viewport.scrollRect = new Rectangle(0, 0, groupWidth + 1, viewHeight);
      scrollBar.height = viewHeight;
      scrollBar.setScrollProperties(viewHeight, 0, Math.max(0, contentHeight - viewHeight), 28);
      scrollBar.position = Math.min(scrollBar.position, Math.max(0, contentHeight - viewHeight));
      scrollBar.visible = needsScroll;
      scrollBar.validateNow();
      onScroll(null);
      graphics.clear();
      graphics.lineStyle(1, 0xAEA58B, 0.23);
      graphics.beginFill(0x10110E, 0.80);
      graphics.drawRoundRect(0, 0, PANEL_W, panelHeight, 3);
      graphics.endFill();
      graphics.lineStyle(1, 0xAEA58B, 0.16);
      graphics.moveTo(14, 53);
      graphics.lineTo(PANEL_W - 14, 53);
      if (resized != null) resized();
    }

    private function layoutGroups(groupWidth:int):int {
      var top:int = 0;
      for each (var header:Object in headers) {
        var closed:Boolean = collapsed[header.id];
        var groupTop:int = top;
        header.view.y = groupTop;
        header.label.width = groupWidth - 24;
        App.utils.commons.truncateTextFieldText(header.label, header.title);
        drawHeaderHit(header.titleHit, groupWidth, false);
        header.tooltip.setText(header.help ||
          (header.label.text != header.title ? header.title : ''));
        header.arrow.rotation = closed ? 0 : 90;
        header.view.graphics.clear();
        header.view.graphics.lineStyle(1, 0xAEA58B, 0.13);
        header.view.graphics.moveTo(0, HEADER_H);
        header.view.graphics.lineTo(groupWidth, HEADER_H);
        top += HEADER_H + (closed ? 0 : 10);
        for each (var control:DebugControl in controls) {
          if (control.sectionID != header.id) continue;
          control.setContentWidth(groupWidth - CONTENT_INSET * 2);
          control.visible = !closed;
          if (control.visible) { control.y = top; top += control.rowHeight; }
        }
        if (!closed) top += 10;
        top += 4;
      }
      return Math.max(0, top);
    }

    private function makeLabel(parent:Sprite, text:String, left:int, top:int, size:int,
                  color:uint = 0xE9E2BF):TextField {
      var field:TextField = App.textMgr.createTextField();
      field.defaultTextFormat = new TextFormat('$FieldFont', size, color);
      field.embedFonts = true;
      field.selectable = false;
      field.mouseEnabled = false;
      field.x = left;
      field.y = top;
      field.width = PANEL_W - 72;
      field.height = 25;
      field.text = text;
      parent.addChild(field);
      return field;
    }

    private function onChanged(section:String, id:String, value:Object):void {
      if (interactive && changed != null) changed(section, id, value);
    }

    private function drawHeaderHit(hit:Sprite, width:int, hover:Boolean):void {
      hit.graphics.clear();
      hit.graphics.beginFill(0xE9E2BF, hover ? 0.07 : 0);
      hit.graphics.drawRect(0, 0, width, HEADER_H);
      hit.graphics.endFill();
    }

    private function onHeaderOver(event:MouseEvent):void {
      var hit:Sprite = Sprite(event.currentTarget);
      drawHeaderHit(hit, hit.width, true);
    }

    private function onHeaderOut(event:MouseEvent):void {
      var hit:Sprite = Sprite(event.currentTarget);
      drawHeaderHit(hit, hit.width, false);
    }

    private function onToggle(event:MouseEvent):void {
      if (!interactive) return;
      var id:String = Sprite(event.currentTarget).name;
      if (beforeToggle != null) beforeToggle();
      releaseInput();
      collapsed[id] = !collapsed[id];
      layout();
    }

    private function onScroll(event:Event):void {
      for each (var header:Object in headers) header.tooltip.hide();
      for each (var control:DebugControl in controls) control.releaseInput();
      body.y = -Math.round(scrollBar.position);
    }

    private function onWheel(event:MouseEvent):void {
      if (!interactive || !scrollBar.visible) return;
      releaseInput();
      scrollBar.position -= event.delta * 24;
      event.stopPropagation();
    }

    public function setInteractive(value:Boolean):void {
      if (interactive && !value) releaseInput();
      interactive = value;
      mouseEnabled = mouseChildren = value;
      alpha = value ? 1.0 : 0.60;
    }

    public function releaseInput():void {
      for each (var header:Object in headers) header.tooltip.hide();
      for each (var control:DebugControl in controls) control.releaseInput();
      // Native sliders and scrollbars terminate their stage drag here.
      if (interactive && stage) stage.dispatchEvent(new MouseEvent(MouseEvent.MOUSE_UP));
    }

    private function clearRows():void {
      for each (var control:DebugControl in controls) control.dispose();
      for each (var header:Object in headers) {
        header.tooltip.dispose();
        header.titleHit.removeEventListener(MouseEvent.CLICK, onToggle);
        header.titleHit.removeEventListener(MouseEvent.ROLL_OVER, onHeaderOver);
        header.titleHit.removeEventListener(MouseEvent.ROLL_OUT, onHeaderOut);
      }
      while (body.numChildren) body.removeChildAt(0);
      controls = [];
      headers = [];
    }

    public function dispose():void {
      releaseInput();
      clearRows();
      removeEventListener(MouseEvent.MOUSE_WHEEL, onWheel);
      scrollBar.removeEventListener(Event.SCROLL, onScroll);
      scrollBar.dispose();
      scrollBar = null;
      changed = resized = beforeToggle = null;
      sections = null;
      collapsed = null;
      panelTitle = mouseHint = null;
    }
  }
}
