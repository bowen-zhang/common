import logging
import sys
import threading
import time
import traceback

class EventEmitter(object):

  def __init__(self, *args, **kwargs):
    super(EventEmitter, self).__init__(*args, **kwargs)
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

  def close(self):
    self._event_handlers = None


class Singleton(object):

  @classmethod
  def get_instance(cls):
    if not hasattr(cls, '_singleton_instance'):
      cls._singleton_instance = cls._create_instance()
    return cls._singleton_instance

  @classmethod
  def _create_instance(cls):
    return cls()


class Logging(object):

  def __init__(self, *args, **kwargs):
    super(Logging, self).__init__(*args, **kwargs)
    self._logger = logging.getLogger(self.__class__.__name__)

  @property
  def logger(self):
    return self._logger


class Worker(Logging):

  def __init__(self, *args, **kwargs):
    super(Worker, self).__init__(*args, **kwargs)

  def start(self):
    self._abort = False
    self._thread = threading.Thread(target=self._run)
    self._thread.daemon = True
    self._thread.start()

  def wait(self):
    self._thread.join()

  def stop(self):
    self._abort = True
    if self._thread:
      self._thread.join()
      self._thread = None

  def close(self):
    self.stop()

  def _run(self):
    self._on_start()
    while not self._abort:
      try:
        self._on_run()
      except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        msg = traceback.format_exception(exc_type, exc_value, exc_traceback)
        self.logger.warn('\n'.join(msg))

    self._on_stop()

  def _on_start(self):
    pass

  def _on_run(self):
    time.sleep(1)

  def _on_stop(self):
    pass

