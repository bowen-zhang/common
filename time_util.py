import datetime
import string
import time


def strfdelta(tdelta,
              fmt='{D:02}d {H:02}h {M:02}m {S:02}s',
              inputtype='timedelta'):
  """Convert a datetime.timedelta object or a regular number to a custom-
    formatted string, just like the stftime() method does for datetime.datetime
    objects.

    The fmt argument allows custom formatting to be specified.  Fields can
    include seconds, minutes, hours, days, and weeks.  Each field is optional.

    Some examples:
        '{D:02}d {H:02}h {M:02}m {S:02}s' --> '05d 08h 04m 02s' (default)
        '{W}w {D}d {H}:{M:02}:{S:02}'     --> '4w 5d 8:04:02'
        '{D:2}d {H:2}:{M:02}:{S:02}'      --> ' 5d  8:04:02'
        '{H}h {S}s'                       --> '72h 800s'

    The inputtype argument allows tdelta to be a regular number instead of the
    default, which is a datetime.timedelta object.  Valid inputtype strings:
        's', 'seconds',
        'm', 'minutes',
        'h', 'hours',
        'd', 'days',
        'w', 'weeks'
    """

  # Convert tdelta to integer seconds.
  if inputtype == 'timedelta':
    remainder = int(tdelta.total_seconds())
  elif inputtype in ['s', 'seconds']:
    remainder = int(tdelta)
  elif inputtype in ['m', 'minutes']:
    remainder = int(tdelta) * 60
  elif inputtype in ['h', 'hours']:
    remainder = int(tdelta) * 3600
  elif inputtype in ['d', 'days']:
    remainder = int(tdelta) * 86400
  elif inputtype in ['w', 'weeks']:
    remainder = int(tdelta) * 604800

  f = string.Formatter()
  desired_fields = [field_tuple[1] for field_tuple in f.parse(fmt)]
  possible_fields = ('W', 'D', 'H', 'M', 'S')
  constants = {'W': 604800, 'D': 86400, 'H': 3600, 'M': 60, 'S': 1}
  values = {}
  for field in possible_fields:
    if field in desired_fields and field in constants:
      values[field], remainder = divmod(remainder, constants[field])
  return f.format(fmt, **values)


class Clock(object):
  def now(self):
    raise NotImplementedError()

  def time(self):
    raise NotImplementedError()

  def sleep(self, seconds):
    raise NotImplementedError()

  def wait_for_event(self, event, timeout_sec):
    raise NotImplementedError()


class RealWorldClock(Clock):
  def now(self):
    return datetime.datetime.now()

  def time(self):
    return time.time()

  def sleep(self, seconds):
    time.sleep(seconds)

  def wait_for_event(self, event, timeout_sec):
    return event.wait(timeout_sec)


class MockClock(Clock):
  def __init__(self, now=None, elapse_rate=1000.0):
    self._start_time = datetime.datetime.now()
    self._offset = now or self._start_time
    self._elapse_rate = elapse_rate

  def now(self):
    now = datetime.datetime.now()
    elapsed = now - self._start_time
    return self._offset + elapsed * self._elapse_rate

  def time(self):
    return self.now().timestamp()

  def sleep(self, seconds):
    time.sleep(seconds / self._elapse_rate)

  def wait_for_event(self, event, timeout_sec):
    return event.wait(timeout_sec / self._elapse_rate)


class TestClock(Clock):
  def __init__(self, start_time):
    self._current_time = start_time

  def now(self):
    return self._current_time

  def time(self):
    return self._current_time.timestamp()

  def sleep(self, seconds):
    time.sleep(0.1)

  def wait_for_event(self, event, timeout_sec):
    return event.wait(0.1)

  def set_time(self, time):
    self._current_time = time
