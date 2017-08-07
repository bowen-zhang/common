import collections
import logging
import os
import sys

from common import pattern


def get_terminal_size(fd=1):
  """
  Returns height and width of current terminal. First tries to get
  size via termios.TIOCGWINSZ, then from environment. Defaults to 25
  lines x 80 columns if both methods fail.

  :param fd: file descriptor (default: 1=stdout)
  """
  try:
    import fcntl, termios, struct
    hw = struct.unpack('hh', fcntl.ioctl(fd, termios.TIOCGWINSZ, '1234'))
  except:
    try:
      hw = (os.environ['LINES'], os.environ['COLUMNS'])
    except:
      hw = (25, 80)
  return hw


class Dashboard(pattern.Singleton):

  def __init__(self, *args, **kwargs):
    super(Dashboard, self).__init__(*args, **kwargs)
    self._updating = 0
    self.reset()

  def start_update(self):
    self._updating += 1

  def stop_update(self):
    self._updating -= 1
    if self._updating <= 0:
      sys.stdout.flush()

  def reset(self):
    os.system('clear')

  def set_text(self, x, y, text):
    sys.stdout.write('\x1b7\x1b[{0};{1}f{2}\x1b8'.format(y, x, text))
    self._done()

  def clear(self, x1, y1, x2, y2):
    """Clears area between (x1, y1) and (x2, y2) (both are inclusive)."""
    fill = ' ' * (x2 - x1 + 1)
    self.start_update()
    for y in range(y1, y2 + 1):
      self.set_text(x1, y, fill)
    self.stop_update()

  def _done(self):
    if self._updating <= 0:
      sys.stdout.flush()


class Field(object):

  def __init__(self, *args, **kwargs):
    self._dashboard = Dashboard.get_instance()

  @property
  def dashboard(self):
    return self._dashboard


class TextField(Field):

  def __init__(self, x, y, max_width, max_height=1, fmt=None, *args, **kwargs):
    super(TextField, self).__init__(*args, **kwargs)
    assert x >= 1, 'X must be a positive number.'
    assert y >= 1, 'X must be a positive number.'
    assert max_width > 0, 'Max width must be at least 1 character.'
    self._x = x
    self._y = y
    self._max_width = max_width
    self._max_height = max_height
    self._fmt = fmt

  def clear(self):
    self.dashboard.clear(x, y, x + max_width - 1, y + max_height - 1)

  def set(self, text):
    self._set(self._y, text)

  def set_multi(self, text_list):
    self.dashboard.start_update()
    for i, text in enumerate(text_list):
      self._set(self._y + i, text)
    self.dashboard.stop_update()

  def _set(self, y, text):
    if self._fmt:
      text = self._fmt.format(text)
    else:
      text = str(text)

    if len(text) > self._max_width:
      text = text[0:self._max_width]
    else:
      text += ' ' * (self._max_width - len(text))
    self.dashboard.set_text(self._x, y, text)


class LabeledTextField(TextField):

  def __init__(self, x, y, max_width, label, fmt=None, *args, **kwargs):
    super(LabeledTextField, self).__init__(
        x=x + len(label),
        y=y,
        max_width=max_width - len(label),
        max_height=1,
        fmt=fmt,
        *args,
        **kwargs)
    self.dashboard.set_text(x, y, label)


from common import pattern


class LoggingHandler(pattern.Logger, logging.Handler):

  def __init__(self, y, *args, **kwargs):
    super(LoggingHandler, self).__init__(*args, **kwargs)
    lines, columns = get_terminal_size()
    self._max_lines = lines - y
    self._text_field = TextField(
        x=1, y=y, max_width=columns, max_height=self._max_lines)
    self._buffer = collections.deque()

  def emit(self, record):
    log_entry = self.format(record)
    lines = log_entry.split('\n')
    for line in lines:
      self._buffer.append(line)
    while len(self._buffer) > self._max_lines:
      self._buffer.popleft()
    self._text_field.set_multi(self._buffer)
