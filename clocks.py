import datetime
import ephem
import os
import retrying
import subprocess

from . import pattern


def set_system_time(target):
  """Sets system date time to target (requires root)

  Args:
    target: a datetime object.
  """
  subprocess.call(
      ['sudo', 'date', '-s',
       target.strftime('%Y/%m/%d %H:%M:%S')],
      stdout=subprocess.PIPE,
      stderr=subprocess.PIPE)


class ReplayClock(object):

  def __init__(self, start_time, speed):
    self._start_time = start_time
    self._speed = speed
    self._true_start_time = datetime.datetime.utcnow()

  @property
  def utc(self):
    elapsed = datetime.datetime.utcnow() - self._true_start_time
    elapsed = datetime.timedelta(
        seconds=elapsed.total_seconds() * self._speed)
    return self._start_time + elapsed


class Clock(object):

  def __init__(self, *args, **kwargs):
    self._last_location = None
    self._last_date = None
    self._sunrise = None
    self._sunset = None

  @property
  def utc(self):
    raise NotImplementedError()

  @property
  def local_time(self):
    raise NotImplementedError()

  @property
  def sunrise(self):
    self._update_sunrise_sunset()
    return self._sunrise

  @property
  def sunset(self):
    self._update_sunrise_sunset()
    return self._sunset

  def _get_location(self):
    """Gets current location on earth for local time calculation.

    Returns:
      (latitude, longitude, elevation)
    """
    raise NotImplementedError()

  def _update_sunrise_sunset(self):
    location = self._get_location()
    now = self.local_time
    date = now.strftime('%Y/%m/%d')
    if self._last_location != location or self._last_date != date:
      offset = self.utc - now
      ob = ephem.Observer()
      ob.date = date
      ob.lat, ob.lon, ob.elevation = (str(location[0]), str(location[1]),
                                      location[2])
      sun = ephem.Sun()
      time = ob.next_rising(sun).datetime() - offset
      self._sunrise = datetime.datetime(
          year=now.year,
          month=now.month,
          day=now.day,
          hour=time.hour,
          minute=time.minute)
      time = ob.next_setting(sun).datetime() - offset
      self._sunset = datetime.datetime(
          year=now.year,
          month=now.month,
          day=now.day,
          hour=time.hour,
          minute=time.minute)
      self._last_location = location
      self._last_date = date


class SystemClock(Clock):

  def __init__(self, lat=None, lon=None, elevation=None, *args, **kwargs):
    super(SystemClock, self).__init__(*args, **kwargs)
    self._location = (lat, lon, elevation)

  def _get_location(self):
    return self._location

  @property
  def utc(self):
    return datetime.datetime.utcnow()

  @property
  def local_time(self):
    return datetime.datetime.now()


class GpsClock(Clock, pattern.Logger):
  MIN_TIME = datetime.datetime(2017, 1, 1, 0, 0, 0)
  THRESHOLD = datetime.timedelta(seconds=60)

  def __init__(self, gps, *args, **kwargs):
    super(GpsClock, self).__init__(*args, **kwargs)
    self._gps = gps

    # self._wait_for_local_time()
    self._wait_for_gps_time()
    self.logger.info('System time was {0}.'.format(
        datetime.datetime.utcnow()))
    self.logger.info('Setting system time to {0}...'.format(self._gps.utc))
    os.system(
        'sudo date -s {0:%Y-%m-%dT%H:%M:%S.000Z}'.format(self._gps.utc))
    self.logger.info('System time is {0}.'.format(
        datetime.datetime.utcnow()))
    # self._wait_for_time_match()

    self._time_offset = self._gps.utc - datetime.datetime.utcnow()

  @property
  def utc(self):
    return datetime.datetime.utcnow() + self._time_offset

  @retrying.retry(
      wait_fixed=1000, stop_max_delay=60000, retry_on_exception=lambda x: True)
  def _wait_for_local_time(self):
    if datetime.datetime.utcnow() < self.__class__.MIN_TIME:
      self.logger.debug('Local time not available.')
      raise Exception('Local time not available.')

  @retrying.retry(wait_fixed=1000, retry_on_exception=lambda x: True)
  def _wait_for_gps_time(self):
    if not self._gps.utc:
      self.logger.debug('GPS time not available.')
      raise Exception('GPS time not available.')

  @retrying.retry(
      wait_fixed=1000, stop_max_delay=60000, retry_on_exception=lambda x: True)
  def _wait_for_time_match(self):
    diff = datetime.datetime.utcnow() - self._gps.utc
    if diff > self.__class__.THRESHOLD or diff < -self.__class__.THRESHOLD:
      self.logger.debug('GPS and local time not match.')
      raise Exception('GPS and local time not match.')

  def _get_location(self):
    return (self._gps.latitude, self._gps.longitude, self._gps.altitude)
