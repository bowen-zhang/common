proto-py:
	python3 -m grpc_tools.protoc -I./proto --python_out=./proto --grpc_python_out=./proto proto/*.proto
	sed -i -r 's/^import (.+_pb2.*)/from . import \1/g' ./proto/*_pb2*.py

