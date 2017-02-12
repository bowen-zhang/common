import abc
import datetime
import enum
import traceback
import time
import sys

from common import pattern


class _SubscriberInfo(object):

  def __init__(self, callback, min_interval):
    self.callback = callback
    self.min_interval = min_interval
    self.last_transmission = time.time()


class Pubsub(pattern.Singleton, pattern.Logger):

  def __init__(self, *args, **kwargs):
    super(Pubsub, self).__init__(*args, **kwargs)
    self._topics = {}

  def publish(self, topic, data):
    if topic not in self._topics:
      return

    subscribers_info = self._topics[topic]
    ts = time.time()
    for info in subscribers_info:
      if ts - info.last_transmission >= info.min_interval.total_seconds():
        try:
          info.callback(topic, data)
        except:
          exc_type, exc_value, exc_traceback = sys.exc_info()
          msg = traceback.format_exception(exc_type, exc_value, exc_traceback)
          self.logger.warn('\n'.join(msg))

        info.last_transmission = ts

  def subscribe(self, topic, callback, min_interval=datetime.timedelta(seconds=0)):
    if topic not in self._topics:
      self._topics[topic] = []

    subscribers_info = self._topics[topic]
    info = [x for x in subscribers_info if x.callback == callback]
    assert not info
    subscribers_info.append(_SubscriberInfo(callback, min_interval))

  def unsubscribe(self, topic, callback):
    assert topic in self._topics

    subscribers_info = self._topics[topic]
    info = [x for x in subscribers_info if x.callback == callback]
    assert info
    subscribers_info.remove(info[0])

    if not subscribers_info:
      del self._topics[topic]


class Publisher(object):
  def __init__(self, *args, **kwargs):
    super(Publisher, self).__init__(*args, **kwargs)
    self._pubsub = Pubsub.get_instance()

  def publish(self, topic, data):
    self._pubsub.publish(topic, data)


class Subscriber(object):
  def __init__(self, *args, **kwargs):
    super(Subscriber, self).__init__(*args, **kwargs)
    self._pubsub = Pubsub.get_instance()

  def subscribe(self, topic, callback):
    self._pubsub.subscribe(topic, callback)

  def unsubscribe(self, topic, callback):
    self._pubsub.unsubscribe(topic, callback)

