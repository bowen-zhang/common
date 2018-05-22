import abc
import logging
import sys
import threading
import time
import traceback


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
    raise NotImplementedError()


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


class Startable(object):
  __metaclass__ = abc.ABCMeta

  def start(self):
    pass


class Stopable(object):
  __metaclass__ = abc.ABCMeta

  def stop(self):
    pass


class Worker(Logger, Closable, Startable, Stopable):
  __metaclass__ = abc.ABCMeta

  def __init__(self, *args, **kwargs):
    super(Worker, self).__init__(*args, **kwargs)
    self._thread = None

  @property
  def is_running(self):
    return self._thread and self._thread.is_alive()

  def start(self):
    assert not self.is_running

    self._abort = False
    self._thread = threading.Thread(target=self._run)
    self._thread.daemon = True
    self._thread.start()

  def wait(self):
    if self.is_running:
      self._thread.join()

  def stop(self):
    self._abort = True
    if self._thread:
      if threading.current_thread() != self._thread:
        self._thread.join()
      self._thread = None

  def close(self):
    self.logger.debug('Closing...')
    if self.is_running:
      self.stop()
    self.logger.debug('Closed.')

  def _run(self):
    if self._on_start() == False:
      self._on_stop()
      return

    while not self._abort:
      try:
        if self._on_run() == False:
          break
      except:
        try:
          exc_type, exc_value, exc_traceback = sys.exc_info()
          msg = traceback.format_exception(exc_type, exc_value, exc_traceback)
          self.logger.warn('\n'.join(msg))
        except:
          pass

    self._on_stop()

  def _on_start(self):
    pass

  def _on_run(self):
    time.sleep(1)

  def _on_stop(self):
    pass

  def _sleep(self, seconds):
    while not self._abort and seconds > 1:
      time.sleep(1)
      seconds -= 1
    if not self._abort and seconds > 0:
      time.sleep(seconds)
