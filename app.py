import configparser
import datetime
import logging
import os
import re
import signal
import sys
import threading
import time
import traceback

from . import pattern
from absl import app as absl_app
from absl import flags
from absl import logging as absl_logging
from google.protobuf import text_format

FLAGS = flags.FLAGS

flags.DEFINE_boolean('log_to_file', False, 'Log to a timestamp-named file.')
flags.DEFINE_string(
    'loglevel', 'INFO',
    'Level of log to output, such as ERROR, WARNING, INFO, DEBUG.')


def start(app_class):
  def _main(_):
    app_class().run()

  absl_app.run(_main)


class UTCFormatter(logging.Formatter):
  converter = time.gmtime


class LogNameFilter(logging.Filter):
  _BLACKLIST = [
      re.compile(r'kafka\..*'),
  ]

  def filter(self, record):
    for pattern in self._BLACKLIST:
      if pattern.match(record.name):
        return False
    return True


class App(pattern.Logger, pattern.Closable):
  def __init__(self,
               name,
               config_path=None,
               config_proto_cls=None,
               *args,
               **kwargs):
    super(App, self).__init__(*args, **kwargs)

    self._name = name
    if config_path and config_proto_cls:
      self._config = config_proto_cls()
      with open(config_path, 'r') as f:
        config_text = f.read()
        text_format.Merge(config_text, self._config)
    else:
      self._config = None

    self._old_signal_handler = signal.signal(
        signal.SIGINT, self._signal_handler)

  @property
  def name(self):
    return self._name

  @property
  def config(self):
    return self._config

  def init_logging(self, log_path, console_handler=logging.StreamHandler()):
    if not os.path.isdir(log_path):
      os.makedirs(log_path)

    log_level = getattr(logging, FLAGS.loglevel.upper(), None)

    root = logging.getLogger('')
    root.removeHandler(absl_logging._absl_handler)
    root.setLevel(logging.DEBUG)
    logfile_formatter = UTCFormatter(
        fmt='%(levelname)-8s %(asctime)s %(name)-12s %(message)s',
        datefmt='%m%d %H:%M:%S')

    if FLAGS.log_to_file:
      timestamp = '.{0:%Y%m%d.%H%M%S}'.format(datetime.datetime.utcnow())
      all = logging.FileHandler(
          os.path.join(log_path, self.name + timestamp + '.all'))
      all.setLevel(logging.DEBUG)
      all.addFilter(LogNameFilter())
      all.setFormatter(logfile_formatter)
      root.addHandler(all)

      warning = logging.FileHandler(
          os.path.join(log_path, self.name + timestamp + '.wrn'))
      warning.setLevel(logging.WARNING)
      warning.setFormatter(logfile_formatter)
      root.addHandler(warning)

      error = logging.FileHandler(
          os.path.join(log_path, self.name + timestamp + '.err'))
      error.setLevel(logging.ERROR)
      error.setFormatter(logfile_formatter)
      root.addHandler(error)

    if console_handler:
      console_handler.setLevel(log_level)
      console_handler.addFilter(LogNameFilter())
      console_handler.setFormatter(
          logging.Formatter('%(levelname)1.1s %(name)-16s: %(message)s'))
      root.addHandler(console_handler)

  def run(self):
    pass

  def close(self):
    self.logger.info('Exiting app...')
    logging.shutdown()

  def shutdown(self, exitcode=0):
    self.close()
    sys.exit(exitcode)

  def _signal_handler(self, signal, frame):
    self.logger.warn('Aborting...')
    if self._old_signal_handler:
      # First time, assume app can terminate background threads properly and exit on its own.
      handler = self._old_signal_handler
      self._old_signal_handler = None
      handler(signal, frame)
    else:
      # Second time, force to exit.
      for thread_id, stack in sys._current_frames().items():
        self.logger.info('Thread: %s', thread_id)
        for filename, lineno, name, line in traceback.extract_stack(stack):
          self.logger.info('%s:L%s', filename, lineno)
      self.shutdown(-1)


class Config(object):
  def __init__(self, config_path, default_section=None):
    self._config = configparser.ConfigParser()
    self._config.read(config_path)
    self._default_section = default_section

  @property
  def default_section(self):
    return self._default_section

  def set_default_section(self, section):
    self._default_section = section

  def get(self, section, key, default_value=None):
    if self._default_section:
      name = section + '.' + key
      if self._config.has_option(self._default_section, name):
        return self._config.get(self._default_section, name)

    if self._config.has_option(section, key):
      return self._config.get(section, key)
    else:
      return default_value

  def get_int(self, section, key, default_value=None):
    value = self.get(section, key)
    return int(value) if value else default_value

  def get_bool(self, section, key, default_value=None):
    true_set = ['true', '1', 'y', 'yes']
    value = self.get(section, key)
    return value.lower() in true_set if value else default_value

  def get_float(self, section, key, default_value=None):
    value = self.get(section, key)
    return float(value) if value else default_value

  def get_raw(self, section, key):
    return self._config.get(section, key)

  def has_section(self, section):
    return self._config.has_section(section)

  def has(self, section, key):
    if self._default_section:
      name = section + '.' + key
      if self._config.has_option(self._default_section, name):
        return True

    return self._config.has_option(section, key)
