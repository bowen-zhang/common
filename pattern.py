import abc
import logging
import sys
import threading
import traceback

from . import time_util


class EventEmitter(object):
  def __init__(self, *args, **kwargs):
    super(EventEmitter, self).__init__()
    self._event_handlers = {}

  def on(self, event, callback):
    assert self._event_handlers is not None

    if event not in self._event_handlers:
      self._event_handlers[event] = []
    self._event_handlers[event].append(callback)

  def off(self, event, callback):
    assert self._event_handlers is not None

    if event in self._event_handlers:
      del self._event_handlers[event]

  def emit(self, event, *args, **kwargs):
    assert self._event_handlers is not None

    if event in self._event_handlers:
      for handler in self._event_handlers[event]:
        handler(*args, **kwargs)

  def emit_after(self, delay, event, *args, **kwargs):
    """Emits an event only after a delay.

    Args:
      delay: in seconds
      event: event name to emit.
      *args: unnamed arguments associated with the event.
      **kwargs: named arguments associated with the event.
    Returns:
      threading.Timer() object. To cancel the emit, call .cancel().
    """
    t = threading.Timer(delay, self.emit, *args, **kwargs)
    t.start()
    return t

  def close(self):
    self._event_handlers = None


class Closable(object):
  def __init__(self, *args, **kwargs):
    super(Closable, self).__init__()

  def __enter__(self):
    return self

  def __exit__(self, type, value, traceback):
    self.close()

  def close(self):
    pass


class Singleton(object):
  @classmethod
  def get_instance(cls):
    if not hasattr(cls, '_singleton_instance'):
      cls._singleton_instance = cls._create_instance()
    return cls._singleton_instance

  @classmethod
  def _create_instance(cls):
    return cls()


class Logger(object):
  def __init__(self, *args, **kwargs):
    super(Logger, self).__init__()
    self._logger = logging.getLogger(self.__class__.__name__)

  @property
  def logger(self):
    return self._logger


class Startable(object, metaclass=abc.ABCMeta):
  def start(self):
    pass


class Stopable(object, metaclass=abc.ABCMeta):
  def stop(self):
    pass


class Worker(Startable, Stopable, Closable, Logger):
  """Base class to support background thread."""

  def __init__(self, worker_name=None, interval=None, clock=None, *args, **kwargs):
    """Creates a Worker instance.

    Args:
      worker_name: an arbitrary string describing the worker.
      interval: a datetime.timedelta object specifying interval between each _on_run() call.
    """
    super(Worker, self).__init__(*args, **kwargs)
    self._worker_name = worker_name if worker_name else self.__class__.__name__
    self._interval_sec = interval.total_seconds() if interval else 0
    self._clock = clock or time_util.RealWorldClock()
    self._worker_thread = None
    self._abort_event = threading.Event()

  @property
  def is_running(self):
    return self._worker_thread and self._worker_thread.is_alive()

  def start(self):
    if self._worker_thread and self._worker_thread.is_alive():
      return

    self.logger.info('Starting...')
    if self._on_start() == False:
      self.logger.info('Stopping...')
      self._on_stop()
      self.logger.info('Stopped.')
      return

    self._abort_event.clear()
    self._worker_thread = threading.Thread(name=self._worker_name,
                                           target=self._run)
    self._worker_thread.daemon = True
    self._worker_thread.start()

  def stop(self):
    if not self._worker_thread:
      return

    if not self._worker_thread.is_alive():
      self._worker_thread = None
      return

    self._abort_event.set()
    self._worker_thread.join()
    self._worker_thread = None

  def close(self):
    self.stop()

  def _run(self):
    self.logger.info('Started.')

    abort = self._abort_event.is_set()
    while not abort:
      start_time_sec = self._clock.time()

      try:
        if self._on_run() == False:
          break
      except Exception as e:
        try:
          exc_type, exc_value, exc_traceback = sys.exc_info()
          msg = traceback.format_exception(exc_type, exc_value, exc_traceback)
          self.logger.warn('\n'.join(msg))
        except:
          self.logger.warn('Exception: {0}'.format(e))
          pass

      wait_time_sec = start_time_sec + self._interval_sec - self._clock.time()
      if wait_time_sec > 0:
        self._clock.wait_for_event(self._abort_event, wait_time_sec)
      abort = self._abort_event.is_set()

    self.logger.info('Stopping...')
    self._on_stop()
    self.logger.info('Stopped.')

  def _on_start(self):
    pass

  def _on_run(self):
    self._sleep(1)

  def _on_stop(self):
    pass

  def _sleep(self, seconds):
    self._clock.wait_for_event(self._abort_event, seconds)
