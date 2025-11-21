
import os, subprocess, sys
from concurrent import futures
from prometheus_client import start_http_server
import uvicorn
from fastapi import FastAPI
from threading import Thread

def ensure_proto():
    try:
        from coordinator.pb import coordinator_pb2 as _
        from coordinator.pb import coordinator_pb2_grpc as _
    except Exception:
        proto = os.path.join(os.path.dirname(__file__), "..", "protos", "coordinator.proto")
        out = os.path.join(os.path.dirname(__file__), "pb")
        os.makedirs(out, exist_ok=True)
        subprocess.check_call([sys.executable, "-m", "grpc_tools.protoc", "-I", os.path.join(os.path.dirname(__file__), "..", "protos"),
                               f"--python_out={out}", f"--grpc_python_out={out}", proto])
ensure_proto()
from coordinator.pb import coordinator_pb2 as pb
from coordinator.pb import coordinator_pb2_grpc as pb_grpc

admin = FastAPI(title="Mimir Admin")
@admin.get("/healthz")
def healthz(): return {"ok": True}

from model.tiny_transformer import TinyTransformer2L
from model.tokenizer import ByteTokenizer
tok = ByteTokenizer(); model = TinyTransformer2L()


from coordinator.attestation_bind import AttestationEvidence, verify_and_issue_cert
from coordinator.policy import load_policy, admit, PartyAdmission
POLICY = load_policy(os.path.join(os.path.dirname(__file__), "policy.yaml"))
CA_KEY = b""  # supply via env/config in real deployment
CA_CERT = b""
class CoordinatorService(pb_grpc.CoordinatorServicer):
    """
    gRPC service for the MPC coordinator.
    Handles party registration, session creation, and inference requests.
    """

    def RegisterParty(self, request, context): return pb.RegisterAck(ok=True, msg=f"Registered {request.party_id}")
    def CreateSession(self, request, context): return pb.SessionAck(ok=True, msg="session created")
    def SubmitPrompt(self, request, context): return pb.SubmitPromptAck(ok=True, msg="prompt accepted")
    def RunInference(self, request, context):
        ids = []
        for i in range(int(request.max_new_tokens or 8)):
            nxt = model.next_token_secure_index(ids)
            ids.append(nxt)
            yield pb.InferenceEvent(token=pb.Token(token_id=nxt, text=tok.decode([nxt])))
            yield pb.InferenceEvent(timing=pb.StepTiming(step_index=i, ms=5.0))
    def FetchMetrics(self, request, context): return pb.Metrics(tokens_per_second=0.0, triple_pool_remaining=0)

def start_admin(host="0.0.0.0", port=8081):
    """
    Start the admin FastAPI server.
    """
    uvicorn.run(admin, host=host, port=port, log_level="warning")

def serve(address="0.0.0.0:8080", metrics_port=9090, admin_port=8081):
    """
    Start the main gRPC server and auxiliary services.
    
    Args:
        address: gRPC server bind address.
        metrics_port: Prometheus metrics port.
        admin_port: Admin API port.
    """
    start_http_server(metrics_port)
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=8))
    pb_grpc.add_CoordinatorServicer_to_server(CoordinatorService(), server)
    creds = tls_server_creds()
    (server.add_secure_port(address, creds) if creds else server.add_insecure_port(address))
    server.start()
    Thread(target=start_admin, args=("0.0.0.0", admin_port), daemon=True).start()
    print(f"[coordinator] gRPC: {address} | /metrics: :{metrics_port} | /admin: :{admin_port}")
    server.wait_for_termination()
if __name__ == "__main__":
    serve()
