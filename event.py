import queue
import grpc
import retrying
import threading
import time

from common import auth
from common import pattern
from common.proto import event_pb2
from common.proto import event_pb2_grpc
from google.protobuf import empty_pb2


class _ClientInfo(object):
  def __init__(self):
    self._events = queue.Queue(maxsize=100)

  @property
  def events(self):
    return self._events


class EventService(event_pb2_grpc.EventServiceServicer, pattern.Logger,
                   pattern.Stopable):
  def __init__(self, server, *args, **kwargs):
    super(EventService, self).__init__(*args, **kwargs)
    self._clients = {}
    self._lock = threading.Lock()
    self._abort = False

    event_pb2_grpc.add_EventServiceServicer_to_server(self, server)

  def stop(self):
    self._abort = True
    with self._lock:
      for client in self._clients:
        client.events.put(None)
    super(EventService, self).stop()

  def Ping(self, request, context):
    return empty_pb2.Empty()

  def Send(self, request_iterator, context):
    for event in request_iterator:
      self.logger.debug('Broadcasting event: [{0}] "{1}"...'.format(
          event.client.id, event.name))
      with self._lock:
        for client_id, client_info in self._clients.items():
          if client_info.events.full():
            client_info.events.get()
          client_info.events.put(event)
    return empty_pb2.Empty()

  def Listen(self, client_id, context):
    events = None
    with self._lock:
      if client_id.id not in self._clients:
        self.logger.debug('Adding client {0} for event streaming...'.format(
            client_id.id))
        self._clients[client_id.id] = _ClientInfo()
      events = self._clients[client_id.id].events

    try:
      while context.is_active() and not self._abort:
        try:
          event = events.get(block=True, timeout=5)
          if event:
            yield event
        except queue.Empty as e:
          pass
    except Exception as e:
      print(e)
      with self._lock:
        if client_id.id in self._clients:
          self.logger.debug('Removing client {0}...'.format(client_id.id))
          del self._clients[client_id.id]

    self.logger.debug('Stopped listen stream for client {0}.'.format(
        client_id.id))


class EventClient(pattern.EventEmitter, pattern.Worker):
  def __init__(self, client_id, grpc_channel, *args, **kwargs):
    super(EventClient, self).__init__(*args, **kwargs)
    self._client = event_pb2.Client(id=client_id)
    self._grpc_channel = grpc_channel
    self._stub = None
    self._listen_response = None
    self._send_future = None
    self._events = None

  def send(self, name):
    if self._events:
      self._events.put(name)
    self.emit('event', self._client.id, name)

  def _on_start(self):
    self._connect()

  def _on_stop(self):
    self._disconnect()

  def _on_run(self):
    if not self._stub:
      self._connect()

    if self._stub:
      try:
        self._stub.Ping(empty_pb2.Empty())
      except:
        self._disconnect()

    self._sleep(5)

  def _connect(self):
    self.logger.info('Connecting...')

    self._stub = event_pb2_grpc.EventServiceStub(self._grpc_channel)
    try:
      self._stub.Ping(empty_pb2.Empty())
    except grpc.RpcError as e:
      if e.code() == grpc.StatusCode.UNAVAILABLE:
        self.logger.error('Server not available.')
        self._stub = None
        return False
      else:
        raise

    self.logger.info('Connected')
    self._events = queue.Queue(maxsize=100)
    self._send_future = self._stub.Send.future(self._get_events())
    self._listen_response = self._stub.Listen(self._client)
    threading.Thread(name='EventClient', target=self._listen).start()
    return True

  def _disconnect(self):
    self.logger.info('Disconnecting...')
    self._stub = None

    # Stopping transmitting call
    if self._send_future:
      self._events.put(None)
      self._send_future.cancel()
      self._send_future = None
    # Stopping listening call
    if self._listen_response:
      self._listen_response.cancel()
      self._listen_response = None

    self._events = None
    self.logger.info('Disconnected.')

  def _listen(self):
    self.logger.debug('Starting to listen...')
    try:
      for event in self._listen_response:
        if event.client.id != self._client.id:
          self.emit('event', event.client.id, event.name)
    except grpc.RpcError as e:
      if e.code() == grpc.StatusCode.UNAVAILABLE:
        self.logger.error('Server disconnected.')
      elif e.code() == grpc.StatusCode.CANCELLED:
        # Client stops.
        pass
      else:
        raise

    self.logger.error('Stopped listening.')

  def _get_events(self):
    while self._stub:
      name = self._events.get(block=True)
      if name:
        yield event_pb2.Event(
            client=self._client, timestamp=int(time.time()), name=name)

    self.logger.error('Stopped sending.')
