
import subprocess, sys, os, pytest
@pytest.mark.health
def test_proto_compiles():
    proto = os.path.join(os.path.dirname(__file__), "..", "protos", "coordinator.proto")
    out = os.path.join(os.path.dirname(__file__), "..", "coordinator", "pb")
    os.makedirs(out, exist_ok=True)
    subprocess.check_call([sys.executable, "-m", "grpc_tools.protoc", "-I", os.path.join(os.path.dirname(proto), "..", "protos"),
                           f"--python_out={out}", f"--grpc_python_out={out}", proto])
