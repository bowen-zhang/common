import datetime
import retrying
import os

from common import pattern


class ReplayClock(object):

  def __init__(self, start_time, speed):
    self._start_time = start_time
    self._speed = speed
    self._true_start_time = datetime.datetime.utcnow()

  @property
  def utc(self):
    elapsed = datetime.datetime.utcnow() - self._true_start_time
    elapsed = datetime.timedelta(seconds=elapsed.total_seconds() * self._speed)
    return self._start_time + elapsed


class SystemClock(object):

  @property
  def utc(self):
    return datetime.datetime.utcnow()


class GpsClock(pattern.Logger):
  MIN_TIME = datetime.datetime(2017, 1, 1, 0, 0, 0)
  THRESHOLD = datetime.timedelta(seconds=60)

  def __init__(self, gps, *args, **kwargs):
    super(GpsClock, self).__init__(*args, **kwargs)
    self._gps = gps

    #self._wait_for_local_time()
    self._wait_for_gps_time()
    self.logger.info('System time was {0}.'.format(datetime.datetime.utcnow()))
    self.logger.info('Setting system time to {0}...'.format(self._gps.utc))
    os.system('sudo date -s {0:%Y-%m-%dT%H:%M:%S.000Z}'.format(self._gps.utc))
    self.logger.info('System time is {0}.'.format(datetime.datetime.utcnow()))
    #self._wait_for_time_match()

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
