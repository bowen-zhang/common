import collections
import datetime
import os
import unittest
from unittest import mock

from . import file

File = collections.namedtuple('File', ['name', 'create_time', 'size'])


class BucketManagerTests(unittest.TestCase):
  def _create_files(self, path, files):
    return {os.path.join(path, x.name): x for x in files}

  @mock.patch('os.listdir')
  @mock.patch('os.remove')
  @mock.patch('os.path.isfile')
  @mock.patch('os.path.getctime')
  @mock.patch('os.path.getsize')
  def test_within_max_size(self,
                           mock_os_path_getsize,
                           mock_os_path_getctime,
                           mock_os_path_isfile,
                           mock_os_remove,
                           mock_os_listdir):
    path = '/x/y/z'
    files = self._create_files(path, [
        File('1.txt', datetime.datetime(2019, 1, 1, 0, 0, 0), 1),
        File('2.txt', datetime.datetime(2019, 1, 1, 1, 0, 0), 2),
        File('3.txt', datetime.datetime(2019, 1, 1, 2, 0, 0), 6),
    ])
    mock_os_listdir.return_value=[x.name for x in list(files.values())]
    mock_os_path_isfile.return_value = True
    mock_os_path_getctime.side_effect = lambda path: files[path].create_time
    mock_os_path_getsize.side_effect = lambda path: files[path].size
    m = file.BucketManager(path=path, max_size=10)
    m.cleanup()
    mock_os_remove.assert_not_called()

  @mock.patch('os.listdir')
  @mock.patch('os.remove')
  @mock.patch('os.path.isfile')
  @mock.patch('os.path.getctime')
  @mock.patch('os.path.getsize')
  def test_exceed_max_size(self,
                           mock_os_path_getsize,
                           mock_os_path_getctime,
                           mock_os_path_isfile,
                           mock_os_remove,
                           mock_os_listdir):
    path = '/x/y/z'
    files = self._create_files(path, [
        File('1.txt', datetime.datetime(2019, 1, 1, 0, 0, 0), 1),
        File('2.txt', datetime.datetime(2019, 1, 1, 1, 0, 0), 2),
        File('3.txt', datetime.datetime(2019, 1, 1, 2, 0, 0), 5),
        File('4.txt', datetime.datetime(2019, 1, 1, 3, 0, 0), 6),
    ])
    mock_os_listdir.return_value=[x.name for x in list(files.values())]
    mock_os_path_isfile.return_value = True
    mock_os_path_getctime.side_effect = lambda path: files[path].create_time
    mock_os_path_getsize.side_effect = lambda path: files[path].size
    m = file.BucketManager(path=path, max_size=10)
    m.cleanup()
    mock_os_remove.assert_has_calls(
        [mock.call('/x/y/z/3.txt'),
         mock.call('/x/y/z/2.txt'),
         mock.call('/x/y/z/1.txt')])


if __name__ == '__main__':
  unittest.main()