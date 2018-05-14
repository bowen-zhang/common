import abc
import datetime
from concurrent import futures
import enum
import grpc
import Queue
import threading
import traceback
import time
import sys

from google.protobuf.internal import python_message

from common import clocks
from common import io
from common import pattern
from common.proto import pubsub_pb2
from common.proto import pubsub_pb2_grpc


class _SubscriberInfo(object):

  def __init__(self, callback, min_interval):
    self.callback = callback
    self.min_interval = min_interval
    self.last_transmission = time.time()


class Pubsub(pattern.Singleton, pattern.Logger):

  def __init__(self, *args, **kwargs):
    super(Pubsub, self).__init__(*args, **kwargs)
    self._topics = {}
    self._default_subscribers = []

  def publish(self, topic, data):
    if topic in self._topics:
      self._publish(self._topics[topic], topic, data)
    if self._default_subscribers:
      self._publish(self._default_subscribers, topic, data)

  def subscribe(self, topic, callback, min_interval=None):
    if topic:
      if topic not in self._topics:
        self._topics[topic] = []
      self._subscribe(self._topics[topic], callback, min_interval)
    else:
      self._subscribe(self._default_subscribers, callback, min_interval)

  def unsubscribe(self, topic, callback):
    if topic:
      assert topic in self._topics
      self._unsubscribe(self._topics[topic], callback)
    else:
      self._unsubscribe(self._default_subscribers, callback)

  def _publish(self, subscribers, topic, data):
    ts = time.time()
    for info in subscribers:
      if ts - info.last_transmission >= info.min_interval.total_seconds():
        try:
          info.callback(topic, data)
        except:
          exc_type, exc_value, exc_traceback = sys.exc_info()
          msg = traceback.format_exception(exc_type, exc_value, exc_traceback)
          self.logger.warn('\n'.join(msg))

        info.last_transmission = ts

  def _subscribe(self, subscribers, callback, min_interval):
    info = [x for x in subscribers if x.callback == callback]
    assert not info

    if not min_interval:
      min_interval = datetime.timedelta(seconds=0)

    subscribers.append(_SubscriberInfo(callback, min_interval))

  def _unsubscribe(self, subscribers, callback):
    info = [x for x in subscribers if x.callback == callback]
    assert info
    subscribers.remove(info[0])


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


"""For pubsub over network:

  Master Machine                                                                 Slave Machine(s)
   Local Pubsub                                                                    Local Pubsub
     => _PubsubReceiver => PubsubServer --[grpc]--> PubsubClient => _PubsubTransmitter =>
     <= _PubsubTransmitter <= PubsubServer <--[grpc]-- PubsubClient <= _PubsubReceiver <=
"""

_topic_enum_class = None
_serializer_classes = {}
_message_classes = {}


def init_topic_enum(enum_cls):
  global _topic_enum_class
  _topic_enum_class = enum_cls


def register_serializer(topic_id, serializer_cls):
  global _serializer_classes
  _serializer_classes[topic_id] = serializer_cls


def register_message(topic_id, message_cls):
  global _message_classes
  _message_classes[topic_id] = message_cls


class _PubsubReceiver(Subscriber):
  """Stores topics in queue for dispatching to remote clients."""

  _local = threading.local()

  def __init__(self, topic_ids, *args, **kwargs):
    super(_PubsubReceiver, self).__init__(*args, **kwargs)
    self._topic_ids = topic_ids
    self._topics = Queue.Queue(maxsize=1000)

  @property
  def topics(self):
    return self._topics

  @classmethod
  def disable(cls):
    """Returns a disabler class instance to prevent echo.

    Use it as:
      with _PubsubReceiver.disable():
        # publish topic
    """
    return cls._PubsubReceiverDisabler()

  def __enter__(self):
    self.subscribe(topic=None, callback=self._on_topic)
    return self

  def __exit__(self, exc_type, exc_val, exc_tb):
    self.unsubscribe(topic=None, callback=self._on_topic)

  def reset(self):
    while True:
      try:
        self._topics.get(block=False)
      except Queue.Empty:
        break

  def _on_topic(self, topic_id, data):
    if not self._enabled:
      return
    if self._topic_ids and topic_id not in self._topic_ids:
      return

    topic = pubsub_pb2.Topic()
    if isinstance(topic_id, enum.Enum):
      topic.id = topic_id.value
    else:
      topic.id = topic_id
    topic.timestamp = time.time()
    if isinstance(data, int):
      topic.integer_value = data
    elif isinstance(data, float):
      topic.float_value = data
    elif isinstance(data, str):
      topic.string_value = data
    elif isinstance(data, python_message.GeneratedProtocolMessageType):
      topic.message_value.Pack(data)
    elif isinstance(data, io.Serializer):
      topic.bytes_value = data.serialize()
    else:
      return

    try:
      self._topics.put(topic, block=False)
    except Queue.Full:
      pass

  @property
  def _enabled(self):
    cls = self.__class__
    return not hasattr(cls._local, 'enabled') or cls._local.enabled

  class _PubsubReceiverDisabler(object):

    def __enter__(self):
      _PubsubReceiver._local.enabled = False
      return self

    def __exit__(self, exc_type, exc_val, exc_tb):
      _PubsubReceiver._local.enabled = True


class _PubsubTransmitter(Publisher, pattern.Logger):

  def __init__(self, *args, **kwargs):
    super(_PubsubTransmitter, self).__init__(*args, **kwargs)

  def transmit(self, topic):
    if _topic_enum_class:
      topic_id = _topic_enum_class(topic.id)
    else:
      topic_id = topic.id
    self.logger.debug('Received %s...', topic_id)
    data_type = topic.WhichOneof('data')
    if data_type == 'integer_value':
      data = topic.integer_value
    elif data_type == 'integer_value':
      data = topic.integer_value
    elif data_type == 'float_value':
      data = topic.float_value
    elif data_type == 'string_value':
      data = topic.string_value
    elif data_type == 'bytes_value':
      assert topic_id in _serializer_classes, 'Serializer not registered for topic {0}'.format(
          topic.id)
      data = _serializer_classes[topic_id].deserialize(topic.bytes_value)
    elif data_type == 'message_value':
      assert topic_id in _message_classes, 'Message not registered for topic {0}'.format(
          topic.id)
      data = _message_classes[topic_id]()
      topic.message_value.Unpack(data)
    else:
      return

    with _PubsubReceiver.disable():
      self.logger.debug('Publishing %s...', topic_id)
      self.publish(topic_id, data)


class _PubsubServicer(pubsub_pb2_grpc.PubsubServicer):

  def __init__(self, *args, **kwargs):
    super(_PubsubServicer, self).__init__(*args, **kwargs)
    self._transmitter = _PubsubTransmitter()

  def Register(self, request, context):
    return pubsub_pb2.RegisterResponse(timestamp=time.time())

  def Listen(self, request, context):
    if _topic_enum_class:
      topic_ids = [_topic_enum_class(x) for x in request.topic_id]
    else:
      topic_ids = request.topic_id

    with _PubsubReceiver(topic_ids) as receiver:
      while context.is_active():
        try:
          topic = receiver.topics.get(block=False, timeout=1)
          yield pubsub_pb2.ListenResponse(topic=topic)
        except Queue.Empty:
          pass

  def Dispatch(self, request_iterator, context):
    for request in request_iterator:
      self._transmitter.transmit(request.topic)


class PubsubServer(pattern.Logger, pattern.Singleton):

  _STOP_GRACE_SECS = 5

  def __init__(self, port=50051, *args, **kwargs):
    super(PubsubServer, self).__init__(self, *args, **kwargs)
    self._server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pubsub_pb2_grpc.add_PubsubServicer_to_server(_PubsubServicer(),
                                                 self._server)
    self._server.add_insecure_port('[::]:{0}'.format(port))

  def start(self):
    self.logger.info('Starting Pubsub server...')
    self._server.start()
    self.logger.info('Pubsub server started.')

  def stop(self):
    self.logger.info('Stopping Pubsub server...')
    self._server.stop(grace=self._STOP_GRACE_SECS)
    self.logger.info('Pubsub server stopped.')


class PubsubClient(pattern.Logger):

  def __init__(self,
               service_target,
               inbound_topics=None,
               outbound_topics=None,
               *args,
               **kwargs):
    """Creates a PubsubClient instance to pass given topics between client and server.

    Args:
      service_target: a host:port string for connecting to server.
      inbound_topics: a list of topic ids. Only topics of this list will be received from server.
      outbound_topics: a list of topic ids. Only topics of this list will be sent to server.
    """
    super(PubsubClient, self).__init__(*args, **kwargs)
    self._inbound_topics = inbound_topics
    self._outbound_topics = outbound_topics
    self._transmitter = _PubsubTransmitter()

    self.logger.info('Starting Pubsub client...')
    channel = grpc.insecure_channel(service_target)
    self._stub = pubsub_pb2_grpc.PubsubStub(channel)
    self._register()

    self._abort = False
    self._dispatch_thread = threading.Thread(target=self._dispatch)
    self._listen_thread = threading.Thread(target=self._listen)
    self._dispatch_thread.start()
    self._listen_thread.start()

  def stop(self):
    self._abort = True
    self.logger.info('Stopping dispatching...')
    self._dispatch_thread.join()
    self._dispatch_thread = None
    self.logger.info('Stopping listening...')
    self._listen_thread.join()
    self._listen_thread = None
    self.logger.info('Pubsub client stopped.')

  def _register(self):
    self.logger.info('Registering...')
    request = pubsub_pb2.RegisterRequest()
    response = self._stub.Register(request)

    now = datetime.datetime.fromtimestamp(response.timestamp)
    self.logger.info('Updating system time to %s...', now)
    clocks.set_system_time(now)

  def _listen(self):
    if _topic_enum_class:
      topic_ids = [x.value for x in self._inbound_topics]
    else:
      topic_ids = self._inbound_topics
    request = pubsub_pb2.ListenRequest(topic_id=topic_ids)
    while not self._abort:
      try:
        for response in self._stub.Listen(request):
          self._transmitter.transmit(response.topic)
      except grpc._channel._Rendezvous:
        self.logger.warn('gRPC connection disconnected for listen.')
        pass

  def _dispatch(self):
    while not self._abort:
      try:
        self._stub.Dispatch(self._dispatch_request_iterator())
      except grpc._channel._Rendezvous:
        self.logger.warn('gRPC connection disconnected for dispatch.')
        pass

  def _dispatch_request_iterator(self):
    with _PubsubReceiver(self._outbound_topics) as receiver:
      while not self._abort:
        try:
          topic = receiver.topics.get(block=True, timeout=1)
          self.logger.debug('Dispatching topic %s...', topic.id)
          yield pubsub_pb2.DispatchRequest(topic=topic)
        except Queue.Empty:
          pass
