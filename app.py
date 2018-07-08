import ConfigParser
import datetime
import gflags
import logging
import os
import signal
import sys
import threading
import time

from common import pattern
from google.protobuf import text_format

FLAGS = gflags.FLAGS

gflags.DEFINE_boolean('log_to_file', False, 'Log to a timestamp-named file.')

gflags.DEFINE_string(
    'loglevel', 'INFO',
    'Level of log to output, such as ERROR, WARNING, INFO, DEBUG.')


class UTCFormatter(logging.Formatter):
  converter = time.gmtime


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

    signal.signal(signal.SIGINT, self._signal_handler)

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
    root.setLevel(log_level)
    logfile_formatter = UTCFormatter(
        fmt='%(levelname)-8s %(asctime)s %(name)-12s %(message)s',
        datefmt='%m%d %H:%M:%S')

    if FLAGS.log_to_file:
      timestamp = '.{0:%Y%m%d.%H%M%S}'.format(datetime.datetime.utcnow())
      debug = logging.FileHandler(
          os.path.join(log_path, self.name + timestamp + '.all'))
      debug.setLevel(logging.INFO)
      debug.setFormatter(logfile_formatter)
      root.addHandler(debug)

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
      log_level = getattr(logging, FLAGS.loglevel.upper(), None)
      console_handler.setLevel(log_level)
      console_handler.setFormatter(
          logging.Formatter('%(levelname)-8s %(name)-12s: %(message)s'))
      root.addHandler(console_handler)

  def close(self):
    self.logger.info('Exiting app...')
    logging.shutdown()

  def shutdown(self, exitcode=0):
    self.close()
    sys.exit(exitcode)

  def _signal_handler(self, signal, frame):
    self.logger.warn('Aborting...')
    for thread in threading.enumerate():
      self.logger.debug('Thread: ("{0}")'.format(thread.name))
    self.shutdown(-1)


class Config(object):
  def __init__(self, config_path, default_section=None):
    self._config = ConfigParser.ConfigParser()
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
