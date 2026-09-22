# coding: utf-8

def getMinimapBounds(bounds):
  """Match StoryModeMinimapComponent's full texture bounds on narrow maps."""
  lower, upper = bounds
  width, height = upper[0] - lower[0], upper[1] - lower[1]
  if abs(width - height) < 0.01:
    return bounds

  axis = 0 if width > height else 1
  return ((lower[axis], lower[axis]), (upper[axis], upper[axis]))
