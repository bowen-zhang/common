#!/bin/bash
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. event.proto
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. pubsub.proto
