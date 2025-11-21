
PROTO_DIR=protos
PB_OUT=coordinator/pb
proto:
	python -m grpc_tools.protoc -I $(PROTO_DIR) --python_out=$(PB_OUT) --grpc_python_out=$(PB_OUT) $(PROTO_DIR)/coordinator.proto
