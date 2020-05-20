import pickle
from kazoo import client

from .. import pattern


class Context(pattern.Logger):
  def __init__(self, zookeeper_host, *args, **kwargs):
    super().__init__(self, *args, **kwargs)

    self.logger.info('Connecting to Zookeeper...')
    self._zookeeper_client = client.KazooClient(hosts=zookeeper_host)
    self._zookeeper_client.start()
    self.logger.info('Connected.')

    self._old_values = {}

  def set_config(self, path, value):
    self._zookeeper_client.ensure_path(path)
    self._zookeeper_client.set(path, pickle.dumps(value))

  def get_config(self, path, default_value):
    self._zookeeper_client.ensure_path(path)
    data, _ = self._zookeeper_client.get(path)
    return pickle.loads(data) if data else default_value

  def watch_config(self, path, default_value, callback):
    def _on_value_change(data, stat):
      key = (path, callback)
      new_value = pickle.loads(data) if data else default_value
      if key in self._old_values:
        old_value = self._old_values[key]
        if old_value != new_value:
          callback(new_value, old_value)
      else:
        callback(new_value, None)
      self._old_values[key] = new_value

    self._zookeeper_client.DataWatch(path, func=_on_value_change)
