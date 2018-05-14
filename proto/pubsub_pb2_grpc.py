# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
import grpc

import pubsub_pb2 as pubsub__pb2


class PubsubStub(object):
  # missing associated documentation comment in .proto file
  pass

  def __init__(self, channel):
    """Constructor.

    Args:
      channel: A grpc.Channel.
    """
    self.Register = channel.unary_unary(
        '/common.Pubsub/Register',
        request_serializer=pubsub__pb2.RegisterRequest.SerializeToString,
        response_deserializer=pubsub__pb2.RegisterResponse.FromString,
        )
    self.Listen = channel.unary_stream(
        '/common.Pubsub/Listen',
        request_serializer=pubsub__pb2.ListenRequest.SerializeToString,
        response_deserializer=pubsub__pb2.ListenResponse.FromString,
        )
    self.Dispatch = channel.stream_unary(
        '/common.Pubsub/Dispatch',
        request_serializer=pubsub__pb2.DispatchRequest.SerializeToString,
        response_deserializer=pubsub__pb2.DispatchResponse.FromString,
        )


class PubsubServicer(object):
  # missing associated documentation comment in .proto file
  pass

  def Register(self, request, context):
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

  def Dispatch(self, request_iterator, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')


def add_PubsubServicer_to_server(servicer, server):
  rpc_method_handlers = {
      'Register': grpc.unary_unary_rpc_method_handler(
          servicer.Register,
          request_deserializer=pubsub__pb2.RegisterRequest.FromString,
          response_serializer=pubsub__pb2.RegisterResponse.SerializeToString,
      ),
      'Listen': grpc.unary_stream_rpc_method_handler(
          servicer.Listen,
          request_deserializer=pubsub__pb2.ListenRequest.FromString,
          response_serializer=pubsub__pb2.ListenResponse.SerializeToString,
      ),
      'Dispatch': grpc.stream_unary_rpc_method_handler(
          servicer.Dispatch,
          request_deserializer=pubsub__pb2.DispatchRequest.FromString,
          response_serializer=pubsub__pb2.DispatchResponse.SerializeToString,
      ),
  }
  generic_handler = grpc.method_handlers_generic_handler(
      'common.Pubsub', rpc_method_handlers)
  server.add_generic_rpc_handlers((generic_handler,))