import grpc
import retrying
import Queue
import threading
import time

from common import auth
from common import pattern
from google.protobuf import empty_pb2
from common.proto import event_pb2
from common.proto import event_pb2_grpc


class _ClientInfo(object):
  def __init__(self):
    self._events = Queue.Queue(maxsize=100)

  @property
  def events(self):
    return self._events


class EventService(event_pb2_grpc.EventServiceServicer, pattern.Logger):
  def __init__(self, server, *args, **kwargs):
    super(EventService, self).__init__(*args, **kwargs)
    self._clients = {}
    self._lock = threading.Lock()

    event_pb2_grpc.add_EventServiceServicer_to_server(self, server)

  def Ping(self, request, context):
    return empty_pb2.Empty()

  def Send(self, request_iterator, context):
    for event in request_iterator:
      self.logger.debug('Broadcasting event: [{0}] "{1}"...'.format(
          event.client.id, event.name))
      with self._lock:
        for client_id, client_info in self._clients.iteritems():
          if event.client.id != client_id:
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
      while context.is_active():
        try:
          yield events.get(block=True, timeout=60)
        except Queue.Empty as e:
          pass
    except Exception as e:
      print e
      with self._lock:
        if client_id.id in self._clients:
          self.logger.debug('Removing client {0}...'.format(client_id.id))
          del self._clients[client_id.id]

    self.logger.debug('Stopped listen stream for client {0}.'.format(
        client_id.id))


class EventClient(pattern.EventEmitter, pattern.Worker):
  def __init__(self, client_id, server_host, server_port, *args, **kwargs):
    super(EventClient, self).__init__(*args, **kwargs)
    self._client_id = event_pb2.Client(id=client_id)
    self._target = '{0}:{1}'.format(server_host, server_port)
    self._stub = None
    self._listen_response = None
    self._send_future = None
    self._events = None

  def send(self, name):
    if self._events:
      self._events.put(name)

  def _on_start(self):
    self._connect()

  def _on_stop(self):
    self._disconnect()

  def _on_run(self):
    self._sleep(5)

    if not self._stub:
      if not self._connect():
        return

    try:
      self._stub.Ping(empty_pb2.Empty())
    except:
      self._disconnect()

  def _connect(self):
    self.logger.info('Connecting to {0}...'.format(self._target))

    channel = grpc.insecure_channel(self._target)
    self._stub = event_pb2_grpc.EventServiceStub(channel)
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
    self._events = Queue.Queue(maxsize=100)
    self._send_future = self._stub.Send.future(self._get_events())
    self._listen_response = self._stub.Listen(self._client_id)
    threading.Thread(target=self._listen).start()
    return True

  def _disconnect(self):
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

  def _listen(self):
    self.logger.debug('Starting to listen...')
    try:
      for event in self._listen_response:
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
            client=self._client_id, timestamp=int(time.time()), name=name)

    self.logger.error('Stopped sending.')
