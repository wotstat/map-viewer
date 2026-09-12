# coding: utf-8
"""Public, client-independent settings API for the local map viewer.

registerSection(id, title, controls, onChange): onChange(controlID, value).
setValue updates a displayed value without invoking its owner's callback.
Sections live until unregisterSection or client shutdown; no files are written.
"""
import copy
import logging
import math
from collections import OrderedDict

log = logging.getLogger('WOTSTAT_MAP_VIEWER')


def _text(value, field):
    if not isinstance(value, basestring) or not value.strip():
        raise ValueError('%s must be a non-empty string' % field)
    return value


def _number(value):
    if not isinstance(value, (int, long, float)) or isinstance(value, bool):
        return False
    try:
        return not math.isnan(value) and not math.isinf(value)
    except OverflowError:
        return False


def _validValue(control, value):
    kind = control['type']
    if kind == 'text':
        return False
    if kind == 'slider':
        return _number(value) and control['min'] <= value <= control['max']
    if kind == 'checkbox':
        return isinstance(value, bool)
    return any(value == option['value'] for option in control['options'])


def _control(data):
    if not isinstance(data, dict):
        raise ValueError('Each control must be a dictionary')
    tooltip = data.get('tooltip', '')
    if not isinstance(tooltip, basestring):
        raise ValueError('Tooltip must be a string')
    if data.get('type') == 'text':
        color = data.get('color', 0xC9C9B6)
        if not isinstance(color, (int, long)) or isinstance(color, bool) or not 0 <= color <= 0xFFFFFF:
            raise ValueError('Text color must be an RGB integer')
        return dict(id=_text(data.get('id'), 'control id'), type='text',
                    text=_text(data.get('text'), 'text'), color=color, tooltip=tooltip)
    result = dict(id=_text(data.get('id'), 'control id'),
                  label=_text(data.get('label'), 'control label'), type=data.get('type'), tooltip=tooltip)
    if result['type'] == 'slider':
        low, high, step = data.get('min'), data.get('max'), data.get('step', 1)
        if not all(_number(v) for v in (low, high, step)) or low >= high or step <= 0:
            raise ValueError('Slider requires finite min < max and step > 0')
        suffix = data.get('suffix', '')
        if not isinstance(suffix, basestring):
            raise ValueError('Slider suffix must be a string')
        result.update(min=low, max=high, step=step, suffix=suffix)
    elif result['type'] == 'dropdown':
        options = data.get('options')
        if not isinstance(options, (list, tuple)) or not options:
            raise ValueError('Dropdown requires a non-empty options list')
        result['options'] = []
        for option in options:
            if not isinstance(option, dict):
                raise ValueError('Dropdown options must be dictionaries')
            value = option.get('value')
            if not isinstance(value, (basestring, bool)) and not _number(value):
                raise ValueError('Dropdown values must be strings, booleans or finite numbers')
            if any(value == item['value'] for item in result['options']):
                raise ValueError('Dropdown option values must be unique')
            result['options'].append(dict(label=_text(option.get('label'), 'option label'), value=value))
    elif result['type'] != 'checkbox':
        raise ValueError('Supported control types: slider, checkbox, dropdown')
    if 'value' not in data or not _validValue(result, data['value']):
        raise ValueError('Invalid initial value for control %s' % result['id'])
    result['value'] = data['value']
    return result


class SettingsRegistry(object):
    def __init__(self):
        self._sections = OrderedDict()
        self._listeners = []

    def registerSection(self, sectionID, title, controls, onChange, tooltip=''):
        _text(sectionID, 'section id')
        _text(title, 'section title')
        if not isinstance(tooltip, basestring):
            raise ValueError('Section tooltip must be a string')
        if not callable(onChange):
            raise ValueError('onChange must be callable')
        if not isinstance(controls, (list, tuple)):
            raise ValueError('controls must be a list')
        prepared = OrderedDict()
        for data in controls:
            control = _control(data)
            if control['id'] in prepared:
                raise ValueError('Control ids must be unique within a section')
            prepared[control['id']] = control
        self._sections[sectionID] = dict(title=title, controls=prepared, callback=onChange, tooltip=tooltip)
        self._emit('sections')

    def unregisterSection(self, sectionID):
        if sectionID in self._sections:
            del self._sections[sectionID]
            self._emit('sections')

    def snapshot(self):
        return [dict(id=key, title=section['title'], tooltip=section['tooltip'], controls=copy.deepcopy(section['controls'].values()))
                for key, section in self._sections.iteritems()]

    def getValue(self, sectionID, controlID):
        return self._sections[sectionID]['controls'][controlID]['value']

    def setValue(self, sectionID, controlID, value):
        control = self._sections[sectionID]['controls'][controlID]
        if not _validValue(control, value):
            raise ValueError('Invalid value for %s/%s' % (sectionID, controlID))
        if control['value'] != value:
            control['value'] = value
            self._emit('value', sectionID, controlID, value)

    def changeValue(self, sectionID, controlID, value):
        section = self._sections.get(sectionID)
        if section is None or controlID not in section['controls']:
            return False
        control = section['controls'][controlID]
        if control['type'] == 'text':
            return False
        if not _validValue(control, value):
            self._emit('value', sectionID, controlID, control['value'])
            return False
        if control['value'] == value:
            return True
        try:
            section['callback'](controlID, value)
        except Exception:
            log.exception('Settings callback failed: %s/%s', sectionID, controlID)
            self._emit('value', sectionID, controlID, control['value'])
            return False
        # A callback may unregister or replace its own section.
        if self._sections.get(sectionID) is section:
            self.setValue(sectionID, controlID, value)
        return True

    def subscribe(self, listener):
        if listener not in self._listeners:
            self._listeners.append(listener)

    def unsubscribe(self, listener):
        if listener in self._listeners:
            self._listeners.remove(listener)

    def _emit(self, *event):
        for listener in tuple(self._listeners):
            try:
                listener(*event)
            except Exception:
                log.exception('Settings panel listener failed')


g_registry = SettingsRegistry()
registerSection = g_registry.registerSection
unregisterSection = g_registry.unregisterSection
setValue = g_registry.setValue
getValue = g_registry.getValue
