class SmoothValue(object):
  def __init__(self, window_size):
    self._size = window_size
    self._count = 0
    self._samples = []
    self._next = 0
    self._sum = 0
    self._value = 0

  @property
  def value(self):
    return self._value

  def reset(self):
    self._count = 0
    self._samples = [0] * self._size
    self._next = 0
    self._sum = 0
    self._value = 0

  def set(self, value):
    self._sum += value
    self._sum -= self._samples[self._next % self._size]
    self._samples[self._next] = value
    self._next = (self._next + 1) % self._size
    self._count = self._count + 1 if self._count < self._size else self._size
    self._value = float(self._sum) / self._count