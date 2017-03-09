import ConfigParser
import logging
import os
import signal
import sys
import time

from common import pattern

import gflags

FLAGS = gflags.FLAGS
gflags.DEFINE_string(
  'loglevel', 'DEBUG',
  'Level of log to output, such as ERROR, WARNING, INFO, DEBUG.')


class UTCFormatter(logging.Formatter):
  converter = time.gmtime


class App(pattern.Logger):
  def __init__(self, name, *args, **kwargs):
    super(App, self).__init__(*args, **kwargs)

    self._name = name
    signal.signal(signal.SIGINT, self._signal_handler)

  @property
  def name(self):
    return self._name

  def init_logging(self, log_path):
    if not os.path.isdir(log_path):
      os.makedirs(log_path)

    root = logging.getLogger('')
    root.setLevel(logging.DEBUG)
    logfile_formatter = UTCFormatter(
      fmt='%(levelname)-8s %(asctime)s %(name)-12s %(message)s',
      datefmt='%m%d %H:%M:%S')

    debug = logging.FileHandler(os.path.join(log_path, self.name + '.all'))
    debug.setLevel(logging.DEBUG)
    debug.setFormatter(logfile_formatter)
    root.addHandler(debug)

    warning = logging.FileHandler(os.path.join(log_path, self.name + '.wrn'))
    warning.setLevel(logging.WARNING)
    warning.setFormatter(logfile_formatter)
    root.addHandler(warning)

    error = logging.FileHandler(os.path.join(log_path, self.name + '.err'))
    error.setLevel(logging.ERROR)
    error.setFormatter(logfile_formatter)
    root.addHandler(error)

    console = logging.StreamHandler()
    log_level = getattr(logging, FLAGS.loglevel.upper(), None)
    console.setLevel(log_level)
    console.setFormatter(
      logging.Formatter('%(levelname)-8s %(name)-12s: %(message)s'))
    root.addHandler(console)

  def close(self):
    self.logger.info('Exiting app...')
    logging.shutdown()

  def shutdown(self, exitcode=0):
    self.close()
    sys.exit(exitcode)

  def _signal_handler(self, signal, frame):
    self.logger.warn('Aborting...')
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
