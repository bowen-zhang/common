import grpc
import logging
import random
import sys
import threading
import time

from concurrent import futures

from common import event
from common.proto import event_pb2
from common.proto import event_pb2_grpc

PORT = 9090


def run_server():
  server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
  monitoring_service = event.EventService(server=server)
  server.add_insecure_port('[::]:{0}'.format(PORT))
  server.start()
  raw_input()


def run_client():
  client_id = str(random.randint(0, 10000))
  client = event.EventClient(
      client_id=client_id, server_host='127.0.0.1', server_port=PORT)
  client.on('event', on_event)
  client.start()
  try:
    while True:
      client.send(raw_input('Event name:'))
  finally:
    print 'Stopping...'
    client.stop()


def on_event(client_id, name):
  print '[{0}] {1}'.format(client_id, name)


def main(argv=None):
  root = logging.getLogger('')
  root.setLevel(logging.DEBUG)
  root.addHandler(logging.StreamHandler())

  if argv[1] == 'server':
    #threading.Thread(target=run_server)
    run_server()
  else:
    run_client()


if __name__ == '__main__':
  main(sys.argv)