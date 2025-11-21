
import argparse, os, sys, subprocess
import grpc
def ensure_proto():
    try:
        from coordinator.pb import coordinator_pb2 as _
        from coordinator.pb import coordinator_pb2_grpc as _
    except Exception:
        proto = os.path.join(os.path.dirname(__file__), "..", "protos", "coordinator.proto")
        out = os.path.join(os.path.dirname(__file__), "..", "coordinator", "pb")
        os.makedirs(out, exist_ok=True)
        subprocess.check_call([sys.executable, "-m", "grpc_tools.protoc", "-I", os.path.join(os.path.dirname(__file__), "..", "protos"),
                               f"--python_out={out}", f"--grpc_python_out={out}", proto])
ensure_proto()
from coordinator.pb import coordinator_pb2 as pb
from coordinator.pb import coordinator_pb2_grpc as pb_grpc
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--addr", default="localhost:8080")
    ap.add_argument("--prompt", default="hello"); ap.add_argument("--max-new-tokens", type=int, default=8)
    args = ap.parse_args()
    ch = grpc.insecure_channel(args.addr); stub = pb_grpc.CoordinatorStub(ch)
    req = pb.RunInferenceReq(session_id="s", max_new_tokens=args.max_new_tokens, topk=3)
    for ev in stub.RunInference(req):
        if ev.WhichOneof("ev") == "token":
            sys.stdout.write(ev.token.text); sys.stdout.flush()
    print()
if __name__ == "__main__": main()
