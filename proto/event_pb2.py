# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: event.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='event.proto',
  package='common',
  syntax='proto3',
  serialized_pb=_b('\n\x0b\x65vent.proto\x12\x06\x63ommon\x1a\x1bgoogle/protobuf/empty.proto\"\x14\n\x06\x43lient\x12\n\n\x02id\x18\x01 \x01(\t\"H\n\x05\x45vent\x12\x1e\n\x06\x63lient\x18\x01 \x01(\x0b\x32\x0e.common.Client\x12\x11\n\ttimestamp\x18\x02 \x01(\x05\x12\x0c\n\x04name\x18\x03 \x01(\t2\xa8\x01\n\x0c\x45ventService\x12\x38\n\x04Ping\x12\x16.google.protobuf.Empty\x1a\x16.google.protobuf.Empty\"\x00\x12\x31\n\x04Send\x12\r.common.Event\x1a\x16.google.protobuf.Empty\"\x00(\x01\x12+\n\x06Listen\x12\x0e.common.Client\x1a\r.common.Event\"\x00\x30\x01\x62\x06proto3')
  ,
  dependencies=[google_dot_protobuf_dot_empty__pb2.DESCRIPTOR,])
_sym_db.RegisterFileDescriptor(DESCRIPTOR)




_CLIENT = _descriptor.Descriptor(
  name='Client',
  full_name='common.Client',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='id', full_name='common.Client.id', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=52,
  serialized_end=72,
)


_EVENT = _descriptor.Descriptor(
  name='Event',
  full_name='common.Event',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='client', full_name='common.Event.client', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='timestamp', full_name='common.Event.timestamp', index=1,
      number=2, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='name', full_name='common.Event.name', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=74,
  serialized_end=146,
)

_EVENT.fields_by_name['client'].message_type = _CLIENT
DESCRIPTOR.message_types_by_name['Client'] = _CLIENT
DESCRIPTOR.message_types_by_name['Event'] = _EVENT

Client = _reflection.GeneratedProtocolMessageType('Client', (_message.Message,), dict(
  DESCRIPTOR = _CLIENT,
  __module__ = 'event_pb2'
  # @@protoc_insertion_point(class_scope:common.Client)
  ))
_sym_db.RegisterMessage(Client)

Event = _reflection.GeneratedProtocolMessageType('Event', (_message.Message,), dict(
  DESCRIPTOR = _EVENT,
  __module__ = 'event_pb2'
  # @@protoc_insertion_point(class_scope:common.Event)
  ))
_sym_db.RegisterMessage(Event)


try:
  # THESE ELEMENTS WILL BE DEPRECATED.
  # Please use the generated *_pb2_grpc.py files instead.
  import grpc
  from grpc.framework.common import cardinality
  from grpc.framework.interfaces.face import utilities as face_utilities
  from grpc.beta import implementations as beta_implementations
  from grpc.beta import interfaces as beta_interfaces


  class EventServiceStub(object):

    def __init__(self, channel):
      """Constructor.

      Args:
        channel: A grpc.Channel.
      """
      self.Ping = channel.unary_unary(
          '/common.EventService/Ping',
          request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
          response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
          )
      self.Send = channel.stream_unary(
          '/common.EventService/Send',
          request_serializer=Event.SerializeToString,
          response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
          )
      self.Listen = channel.unary_stream(
          '/common.EventService/Listen',
          request_serializer=Client.SerializeToString,
          response_deserializer=Event.FromString,
          )


  class EventServiceServicer(object):

    def Ping(self, request, context):
      context.set_code(grpc.StatusCode.UNIMPLEMENTED)
      context.set_details('Method not implemented!')
      raise NotImplementedError('Method not implemented!')

    def Send(self, request_iterator, context):
      context.set_code(grpc.StatusCode.UNIMPLEMENTED)
      context.set_details('Method not implemented!')
      raise NotImplementedError('Method not implemented!')

    def Listen(self, request, context):
      context.set_code(grpc.StatusCode.UNIMPLEMENTED)
      context.set_details('Method not implemented!')
      raise NotImplementedError('Method not implemented!')


  def add_EventServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
        'Ping': grpc.unary_unary_rpc_method_handler(
            servicer.Ping,
            request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
            response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
        ),
        'Send': grpc.stream_unary_rpc_method_handler(
            servicer.Send,
            request_deserializer=Event.FromString,
            response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
        ),
        'Listen': grpc.unary_stream_rpc_method_handler(
            servicer.Listen,
            request_deserializer=Client.FromString,
            response_serializer=Event.SerializeToString,
        ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
        'common.EventService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


  class BetaEventServiceServicer(object):
    """The Beta API is deprecated for 0.15.0 and later.

    It is recommended to use the GA API (classes and functions in this
    file not marked beta) for all further purposes. This class was generated
    only to ease transition from grpcio<0.15.0 to grpcio>=0.15.0."""
    def Ping(self, request, context):
      context.code(beta_interfaces.StatusCode.UNIMPLEMENTED)
    def Send(self, request_iterator, context):
      context.code(beta_interfaces.StatusCode.UNIMPLEMENTED)
    def Listen(self, request, context):
      context.code(beta_interfaces.StatusCode.UNIMPLEMENTED)


  class BetaEventServiceStub(object):
    """The Beta API is deprecated for 0.15.0 and later.

    It is recommended to use the GA API (classes and functions in this
    file not marked beta) for all further purposes. This class was generated
    only to ease transition from grpcio<0.15.0 to grpcio>=0.15.0."""
    def Ping(self, request, timeout, metadata=None, with_call=False, protocol_options=None):
      raise NotImplementedError()
    Ping.future = None
    def Send(self, request_iterator, timeout, metadata=None, with_call=False, protocol_options=None):
      raise NotImplementedError()
    Send.future = None
    def Listen(self, request, timeout, metadata=None, with_call=False, protocol_options=None):
      raise NotImplementedError()


  def beta_create_EventService_server(servicer, pool=None, pool_size=None, default_timeout=None, maximum_timeout=None):
    """The Beta API is deprecated for 0.15.0 and later.

    It is recommended to use the GA API (classes and functions in this
    file not marked beta) for all further purposes. This function was
    generated only to ease transition from grpcio<0.15.0 to grpcio>=0.15.0"""
    request_deserializers = {
      ('common.EventService', 'Listen'): Client.FromString,
      ('common.EventService', 'Ping'): google_dot_protobuf_dot_empty__pb2.Empty.FromString,
      ('common.EventService', 'Send'): Event.FromString,
    }
    response_serializers = {
      ('common.EventService', 'Listen'): Event.SerializeToString,
      ('common.EventService', 'Ping'): google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
      ('common.EventService', 'Send'): google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
    }
    method_implementations = {
      ('common.EventService', 'Listen'): face_utilities.unary_stream_inline(servicer.Listen),
      ('common.EventService', 'Ping'): face_utilities.unary_unary_inline(servicer.Ping),
      ('common.EventService', 'Send'): face_utilities.stream_unary_inline(servicer.Send),
    }
    server_options = beta_implementations.server_options(request_deserializers=request_deserializers, response_serializers=response_serializers, thread_pool=pool, thread_pool_size=pool_size, default_timeout=default_timeout, maximum_timeout=maximum_timeout)
    return beta_implementations.server(method_implementations, options=server_options)


  def beta_create_EventService_stub(channel, host=None, metadata_transformer=None, pool=None, pool_size=None):
    """The Beta API is deprecated for 0.15.0 and later.

    It is recommended to use the GA API (classes and functions in this
    file not marked beta) for all further purposes. This function was
    generated only to ease transition from grpcio<0.15.0 to grpcio>=0.15.0"""
    request_serializers = {
      ('common.EventService', 'Listen'): Client.SerializeToString,
      ('common.EventService', 'Ping'): google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
      ('common.EventService', 'Send'): Event.SerializeToString,
    }
    response_deserializers = {
      ('common.EventService', 'Listen'): Event.FromString,
      ('common.EventService', 'Ping'): google_dot_protobuf_dot_empty__pb2.Empty.FromString,
      ('common.EventService', 'Send'): google_dot_protobuf_dot_empty__pb2.Empty.FromString,
    }
    cardinalities = {
      'Listen': cardinality.Cardinality.UNARY_STREAM,
      'Ping': cardinality.Cardinality.UNARY_UNARY,
      'Send': cardinality.Cardinality.STREAM_UNARY,
    }
    stub_options = beta_implementations.stub_options(host=host, metadata_transformer=metadata_transformer, request_serializers=request_serializers, response_deserializers=response_deserializers, thread_pool=pool, thread_pool_size=pool_size)
    return beta_implementations.dynamic_stub(channel, 'common.EventService', cardinalities, options=stub_options)
except ImportError:
  pass
# @@protoc_insertion_point(module_scope)