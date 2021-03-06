# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
import grpc

from . import event_pb2 as event__pb2
from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2


class EventServiceStub(object):
  # missing associated documentation comment in .proto file
  pass

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
        request_serializer=event__pb2.Event.SerializeToString,
        response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
        )
    self.Listen = channel.unary_stream(
        '/common.EventService/Listen',
        request_serializer=event__pb2.Client.SerializeToString,
        response_deserializer=event__pb2.Event.FromString,
        )


class EventServiceServicer(object):
  # missing associated documentation comment in .proto file
  pass

  def Ping(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def Send(self, request_iterator, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def Listen(self, request, context):
    # missing associated documentation comment in .proto file
    pass
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
          request_deserializer=event__pb2.Event.FromString,
          response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
      ),
      'Listen': grpc.unary_stream_rpc_method_handler(
          servicer.Listen,
          request_deserializer=event__pb2.Client.FromString,
          response_serializer=event__pb2.Event.SerializeToString,
      ),
  }
  generic_handler = grpc.method_handlers_generic_handler(
      'common.EventService', rpc_method_handlers)
  server.add_generic_rpc_handlers((generic_handler,))
