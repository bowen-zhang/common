import datetime
import glob
import os


def delete_files(pattern):
  for filepath in glob.iglob(pattern):
    os.remove(filepath)


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
    filename = '{0}_{1:0>3}{2}'.format(self._filename, self._file_no,
                                       self._ext)
    self._file = open(os.path.join(self._path, filename), self._file_mode)
    self._next_flush = datetime.datetime.utcnow(
    ) + ChunkFileWriter.FLUSH_INTERVAL


class ChunkFileReader(object):
  def __init__(self, filepath, file_mode='r'):
    self._path, basename = os.path.split(filepath)
    self._filename, self._ext = os.path.splitext(basename)
    self._file_mode = file_mode
    self._file_no = 0
    self._file = None

  def read(self, size):
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
        filename = '{0}_{1:0>3}{2}'.format(self._filename, self._file_no,
                                           self._ext)
        filepath = os.path.join(self._path, filename)
        if not os.path.isfile(filepath):
          return None
        print(filepath)
        self._file = open(filepath, self._file_mode)

  def close(self):
    if self._file:
      self._file.close()
      self._file = None


class TimedFile(object):
  def __init__(self, path, extension, interval, prefix=None, postfix=None):
    self._path = path
    self._extension = extension
    self._interval = interval
    self._prefix = prefix if prefix else ''
    self._postfix = postfix if postfix else ''
    self._filepath = None
    self._expiration = datetime.datetime.now()

  @property
  def name(self):
    return self._filepath

  def expired(self):
    return datetime.datetime.now() >= self._expiration

  def refresh(self):
    now = datetime.datetime.now()
    midnight = datetime.datetime(now.year, now.month, now.day, 0, 0, 0)
    elapsed = now - midnight
    cycles = int(elapsed.total_seconds() / self._interval.total_seconds())
    timestamp = midnight + datetime.timedelta(
        seconds=self._interval.total_seconds() * cycles)
    self._expiration = midnight + datetime.timedelta(
        seconds=self._interval.total_seconds() * (cycles + 1))

    filename = '{0}{1:%Y%m%dT%H%M%S}{2}.{3}'.format(
        self._prefix, timestamp, self._postfix, self._extension)
    self._filepath = os.path.join(self._path, filename)


class BucketManager(object):
  def __init__(self, path, max_size):
    self._path = path
    self._max_size = max_size

  def cleanup(self):
    filenames = os.listdir(self._path)
    filepaths = [os.path.join(self._path, x) for x in filenames]
    filepaths = [x for x in filepaths if os.path.isfile(x)]
    filepaths.sort(key=lambda x: os.path.getctime(x), reverse=True)
    size = 0
    for filepath in filepaths:
      size += os.path.getsize(filepath)
      if size > self._max_size:
        os.remove(filepath)
