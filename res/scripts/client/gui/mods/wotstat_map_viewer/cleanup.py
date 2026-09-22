# coding: utf-8

class CleanupStack(object):

  def __init__(self):
    self._actions = []

  def defer(self, name, callback, *args):
    self._actions.append((name, callback, args))

  def run(self):
    errors = []
    while self._actions:
      name, callback, args = self._actions.pop()
      try:
        callback(*args)
      except Exception as error:
        errors.append((name, error))
    return errors
