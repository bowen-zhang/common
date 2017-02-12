import datetime
import os


class ChunkFileWriter(object):
  FLUSH_INTERVAL = datetime.timedelta(seconds=60)

  def __init__(self, filepath, file_mode='w', max_size=None):
    self._path, basename = os.path.split(filepath)
    self._filename, self._ext = os.path.splitext(basename)
    self._file_mode = file_mode
    self._max_size = max_size
    self._file_no = 0
    self._file = None
    self._next_flush = None

  def write(self, data):
    if not self._file:
      self._create_file()

    self._file.write(data)
    if self._max_size and self._file.tell() > self._max_size:
      self.close()
    else:
      now = datetime.datetime.utcnow()
      if now > self._next_flush:
        self._file.flush()
        self._next_flush = now + ChunkFileWriter.FLUSH_INTERVAL

  def close(self):
    if self._file:
      self._file.flush()
      self._file.close()
      self._file = None

  def _create_file(self):
    self._file_no += 1
    filename = '{0}_{1:0>3}{2}'.format(self._filename, self._file_no, self._ext)
    self._file = open(os.path.join(self._path, filename), self._file_mode)
    self._next_flush = datetime.datetime.utcnow() + ChunkFileWriter.FLUSH_INTERVAL


class ChunkFileReader(object):
  def __init__(self, filepath, file_mode='r'):
    self._path, basename = os.path.split(filepath)
    self._filename, self._ext = os.path.splitext(basename)
    self._file_mode = file_mode
    self._file_no = 0
    self._file = None

  def read_file(self, size):
    data = ''
    while True:
      if self._file:
        data += self._file.read(size)
        if len(data) == size:
          return data

        self._file.close()
        self._file = None

      if not self._file:
        self._file_no += 1
        filename = '{0}_{1:0>3}{2}'.format(self._filename, self._file_no, self._ext)
        filepath = os.path.join(self._path, filename)
        if not os.path.isfile(filepath):
          return None
        self._file = open(filepath, self._file_mode)

  def close(self):
    if self._file:
      self._file.close()
      self._file = None
