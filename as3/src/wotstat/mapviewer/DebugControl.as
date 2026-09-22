package wotstat.mapviewer {
  import flash.display.Sprite;
  import flash.events.Event;
  import flash.events.FocusEvent;
  import flash.events.MouseEvent;
  import flash.geom.Point;
  import flash.text.TextField;
  import flash.text.TextFormat;
  import flash.text.TextFieldAutoSize;
  import net.wg.gui.components.controls.CheckBox;
  import net.wg.gui.components.controls.DropdownMenu;
  import net.wg.gui.components.controls.Slider;
  import net.wg.gui.components.controls.SoundButtonEx;
  import net.wg.gui.components.controls.UILoaderAlt;
  import scaleform.clik.events.ButtonEvent;
  import scaleform.clik.data.DataProvider;
  import scaleform.clik.events.ListEvent;
  import scaleform.clik.events.SliderEvent;

  public class DebugControl extends Sprite {
    public var sectionID:String;
    public var controlID:String;
    public var rowHeight:int;
    public var slider:Slider;
    public var checkbox:CheckBox;
    public var dropdown:DropdownMenu;
    private var model:Object;
    private var changed:Function;
    private var updating:Boolean = false;
    private var contentWidth:int;
    private var contentLabel:TextField;
    private var valueLabel:TextField;
    private var tooltip:DebugTooltip;
    public var playback:SoundButtonEx;
    private var playbackIcon:UILoaderAlt;
    private var playbackTooltip:DebugTooltip;
    private var dragging:Boolean = false;

    public function DebugControl(section:String, data:Object, w:int, callback:Function) {
      super();
      sectionID = section;
      controlID = data.id;
      model = data;
      changed = callback;
      contentWidth = w;
      name = 'control_' + controlID;
      if (data.type == 'text') {
        var field:TextField = contentLabel = label(data.text, 0, w);
        var textFormat:TextFormat = field.defaultTextFormat;
        textFormat.color = data.color;
        field.defaultTextFormat = textFormat;
        field.multiline = field.wordWrap = true;
        field.autoSize = TextFieldAutoSize.LEFT;
        field.text = data.text;
        rowHeight = Math.ceil(field.height) + 8;
        graphics.beginFill(0, 0);
        graphics.drawRect(0, 0, w, rowHeight);
        graphics.endFill();
      }
      else if (data.type == 'slider' || data.type == 'timeline') {
        contentLabel = label(data.label, 0, w - 96);
        valueLabel = label('', w - 96, 96);
        var format:TextFormat = valueLabel.defaultTextFormat;
        format.align = 'right';
        valueLabel.defaultTextFormat = format;
        slider = App.utils.classFactory.getComponent('Slider', Slider);
        slider.name = 'slider';
        slider.y = 28;
        slider.width = w;
        slider.minimum = data.type == 'timeline' ? 0 : data.min;
        slider.maximum = data.type == 'timeline' ? 100 : data.max;
        slider.snapInterval = data.type == 'timeline' ? 0.1 : data.step;
        slider.snapping = false;
        slider.liveDragging = true;
        addChild(slider);
        slider.validateNow();
        rowHeight = 61;
        if (data.type == 'timeline') {
          contentLabel.multiline = contentLabel.wordWrap = true;
          contentLabel.autoSize = TextFieldAutoSize.LEFT;
          playback = App.utils.classFactory.getComponent('ButtonNormal', SoundButtonEx);
          playback.name = 'playback';
          playback.label = '';
          playback.width = 32;
          playback.height = 24;
          addChild(playback);
          playback.validateNow();
          playbackIcon = new UILoaderAlt();
          playbackIcon.mouseEnabled = playbackIcon.mouseChildren = false;
          playbackIcon.autoSize = true;
          // The native icons are 24x24. Keep that as the loader size and
          // scale its container immediately so an async source swap cannot
          // expose the unscaled icon for one frame.
          playbackIcon.setOriginalWidth(24);
          playbackIcon.setOriginalHeight(24);
          playbackIcon.scaleX = playbackIcon.scaleY = 2 / 3;
          addChild(playbackIcon);
          playbackTooltip = new DebugTooltip(playback, '');
          playback.addEventListener(ButtonEvent.CLICK, onPlayback);
          slider.addEventListener(MouseEvent.MOUSE_DOWN, onSeekStart);
          layoutTimeline(w);
        }
      }
      else if (data.type == 'checkbox') {
        checkbox = App.utils.classFactory.getComponent('CheckBox', CheckBox);
        checkbox.name = 'checkbox';
        checkbox.label = data.label;
        checkbox.width = w;
        checkbox.textSize = 14;
        addChild(checkbox);
        checkbox.validateNow();
        rowHeight = 32;
      }
      else {
        contentLabel = label(data.label, 0, w);
        dropdown = App.utils.classFactory.getComponent('DropdownMenuUI', DropdownMenu);
        dropdown.name = 'dropdown';
        dropdown.y = 26;
        dropdown.width = w;
        dropdown.dropdown = 'DropdownMenu_ScrollingList';
        dropdown.itemRenderer = 'DropDownListItemRendererSound';
        dropdown.menuRowsFixed = false;
        dropdown.rowCount = 8;
        dropdown.menuDirection = 'up';
        dropdown.scrollBar = 'ScrollBar';
        dropdown.dataProvider = new DataProvider(data.options);
        addChild(dropdown);
        dropdown.validateNow();
        rowHeight = 60;
      }
      if (data.type != 'text')
        setValue(data.value);
      tooltip = new DebugTooltip(this, data.tooltip);
      if (slider) {
        slider.addEventListener(SliderEvent.VALUE_CHANGE, onChanged);
        slider.addEventListener(Event.CHANGE, onChanged);
      }
      if (checkbox)
        checkbox.addEventListener(Event.SELECT, onChanged);
      if (dropdown) {
        dropdown.addEventListener(ListEvent.INDEX_CHANGE, onChanged);
        dropdown.addEventListener(FocusEvent.FOCUS_IN, prepareDropdown);
        addEventListener(MouseEvent.MOUSE_DOWN, prepareDropdown, true);
      }
      addEventListener(MouseEvent.MOUSE_WHEEL, onWheel);
    }

    private function label(text:String, left:int, w:int):TextField {
      var field:TextField = App.textMgr.createTextField();
      field.defaultTextFormat = new TextFormat('$FieldFont', 14, 0xC9C9B6);
      field.embedFonts = true;
      field.selectable = false;
      field.mouseEnabled = false;
      field.x = left;
      field.width = w;
      field.height = 24;
      field.text = text;
      addChild(field);
      return field;
    }

    public function setContentWidth(w:int):void {
      if (contentWidth == w)
        return;
      contentWidth = w;
      updating = true;
      if (slider) {
        if (playback)
          layoutTimeline(w);
        else {
          contentLabel.width = w - 96;
          valueLabel.x = w - 96;
          slider.width = w;
          slider.validateNow();
        }
      }
      else if (checkbox) {
        checkbox.width = w;
        checkbox.validateNow();
      }
      else if (dropdown) {
        contentLabel.width = w;
        dropdown.width = w;
        dropdown.validateNow();
      }
      else {
        contentLabel.width = w;
        rowHeight = Math.ceil(contentLabel.height) + 8;
        graphics.clear();
        graphics.beginFill(0, 0);
        graphics.drawRect(0, 0, w, rowHeight);
        graphics.endFill();
      }
      updating = false;
    }

    public function setValue(value:Object):void {
      updating = true;
      model.value = value;
      if (playback) {
        if (!dragging)
          slider.value = Number(value.position);
        var tenths:int = Math.round(Number(value.position) * 10);
        valueLabel.text = String(int(tenths / 10)) + '.' + String(tenths % 10) + '%';
        playbackIcon.source = '../maps/icons/buttons/' + (value.playing ? 'pause' : 'play') + '.png';
        playbackTooltip.setText(value.playing ? model.pauseTooltip : model.playTooltip);
      }
      else if (slider) {
        slider.value = Number(value);
        valueLabel.text = String(Math.round(Number(value) * 100) / 100) + model.suffix;
      }
      else if (checkbox) {
        checkbox.selected = Boolean(value);
        checkbox.validateNow();
      }
      else if (dropdown) {
        for (var i:int = 0; i < model.options.length; ++i) {
          if (model.options[i].value === value) {
            dropdown.selectedIndex = i;
            break;
          }
        }
        dropdown.validateNow();
      }
      updating = false;
    }

    private function onChanged(event:Event):void {
      if (updating)
        return;
      var value:Object;
      if (playback) {
        value = {position: Math.max(0, Math.min(100, Math.round(slider.value * 10) / 10)), playing: false};
        if (changed != null && (value.position != model.value.position || model.value.playing))
          changed(sectionID, controlID, value);
        return;
      }
      else if (slider) {
        if (slider.value <= model.min)
          value = model.min;
        else if (slider.value >= model.max)
          value = model.max;
        else
          value = Math.max(model.min, Math.min(model.max, model.min +
                Math.round((slider.value - model.min) / model.step) * model.step));
      }
      else if (checkbox)
        value = checkbox.selected;
      else {
        if (dropdown.selectedIndex < 0)
          return;
        value = model.options[dropdown.selectedIndex].value;
      }
      if (value !== model.value && changed != null)
        changed(sectionID, controlID, value);
    }

    private function layoutTimeline(w:int):void {
      contentLabel.width = w;
      contentLabel.text = model.label;
      playback.x = 0;
      playback.y = Math.ceil(contentLabel.height) + 4;
      slider.x = 40;
      slider.y = playback.y;
      slider.width = w - 90;
      slider.validateNow();
      valueLabel.x = w - 44;
      valueLabel.y = playback.y;
      valueLabel.width = 44;
      playbackIcon.x = playback.x + 8;
      playbackIcon.y = playback.y + 4;
      rowHeight = Math.ceil(playback.y) + 32;
    }

    private function onPlayback(event:ButtonEvent):void {
      if (!updating && changed != null)
        changed(sectionID, controlID, {position: model.value.position, playing: !model.value.playing});
    }

    private function onSeekStart(event:MouseEvent):void {
      dragging = true;
      if (stage)
        stage.addEventListener(MouseEvent.MOUSE_UP, onSeekEnd);
      if (model.value.playing && changed != null)
        changed(sectionID, controlID, {position: model.value.position, playing: false});
    }

    private function onSeekEnd(event:MouseEvent):void {
      dragging = false;
      if (stage)
        stage.removeEventListener(MouseEvent.MOUSE_UP, onSeekEnd);
    }

    private function onWheel(event:MouseEvent):void {
      // A wheel adjustment must not also scroll the containing panel.
      if (slider && slider.hitTestPoint(event.stageX, event.stageY, true))
        event.stopPropagation();
      if (dropdown && dropdown.hitTestPoint(event.stageX, event.stageY, true))
        event.stopPropagation();
    }

    private function prepareDropdown(event:Event):void {
      if (!dropdown || dropdown.isOpen())
        return;
      var top:Number = dropdown.localToGlobal(new Point()).y / App.appScale;
      var below:Number = App.appHeight - top - dropdown.height - 12;
      var above:Number = top - 12;
      var desired:Number = Math.min(8, model.options.length) * 24 + 8;
      dropdown.menuDirection = below >= desired || below >= above ? 'down' : 'up';
      var room:Number = dropdown.menuDirection == 'down' ? below : above;
      dropdown.rowCount = Math.max(1, Math.min(8, Math.floor((room - 8) / 24)));
    }

    public function releaseInput():void {
      if (tooltip)
        tooltip.hide();
      if (playbackTooltip)
        playbackTooltip.hide();
      onSeekEnd(null);
      if (dropdown)
        dropdown.close();
    }

    public function dispose():void {
      releaseInput();
      tooltip.dispose();
      tooltip = null;
      removeEventListener(MouseEvent.MOUSE_WHEEL, onWheel);
      if (slider) {
        slider.removeEventListener(MouseEvent.MOUSE_DOWN, onSeekStart);
        slider.removeEventListener(SliderEvent.VALUE_CHANGE, onChanged);
        slider.removeEventListener(Event.CHANGE, onChanged);
        slider.dispose();
        slider = null;
      }
      if (playback) {
        playback.removeEventListener(ButtonEvent.CLICK, onPlayback);
        playbackTooltip.dispose();
        playbackTooltip = null;
        removeChild(playbackIcon);
        playbackIcon.dispose();
        playbackIcon = null;
        playback.dispose();
        playback = null;
      }
      if (checkbox) {
        checkbox.removeEventListener(Event.SELECT, onChanged);
        checkbox.dispose();
        checkbox = null;
      }
      if (dropdown) {
        dropdown.removeEventListener(ListEvent.INDEX_CHANGE, onChanged);
        dropdown.removeEventListener(FocusEvent.FOCUS_IN, prepareDropdown);
        removeEventListener(MouseEvent.MOUSE_DOWN, prepareDropdown, true);
        dropdown.dispose();
        dropdown = null;
      }
      changed = null;
      model = null;
      contentLabel = valueLabel = null;
    }
  }
}
