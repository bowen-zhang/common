import datetime
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

    timestamp = '.{0:%Y%m%d.%H%M%S}'.format(datetime.datetime.utcnow())
    debug = logging.FileHandler(
        os.path.join(log_path, self.name + timestamp + '.all'))
    debug.setLevel(logging.DEBUG)
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

    console = logging.StreamHandler()
    log_level = getattr(logging, FLAGS.loglevel.upper(), None)
    console.setLevel(log_level)
    console.setFormatter(
        logging.Formatter('%(levelname)-8s %(name)-12s: %(message)s'))
    root.addHandler(console)

  def shutdown(self, exitcode=0):
    self.logger.info('Shutting down...')
    sys.exit(exitcode)

  def _signal_handler(self, signal, frame):
    self.logger.warn('Aborting...')
    self.shutdown(-1)
