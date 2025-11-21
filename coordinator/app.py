import os
import yaml
import grpc
import stat
from pathlib import Path
from concurrent import futures
from prometheus_client import start_http_server

import mimir_pb2 as pb
import mimir_pb2_grpc as pb_grpc

from .scheduler import AutoRegScheduler
from .attestation import validate_attestation

# ---- Trusted bases (adjust as needed) ----
ROOT_DIR = Path(__file__).resolve().parent
CONFIG_BASE = (ROOT_DIR / "configs").resolve()
CERTS_BASE = (ROOT_DIR / "certs").resolve()

# Allow override via env only as a filename inside CONFIG_BASE (no arbitrary paths)
CFG_FILENAME = os.environ.get("MIMIR_SECURITY_CFG_FILE", "security.yaml")


def _assert_under(base: Path, p: Path) -> None:
    """
    Ensure path p is within base directory.
    Raises ValueError if not.
    """
    try:
        p.relative_to(base)
    except ValueError:
        raise ValueError(f"Refused path outside base: {p}")


def _safe_join(base: Path, rel: str) -> Path:
    """
    Safely join base path with relative path, preventing traversal.
    """
    # Disallow absolute paths and traversal; resolve against base and re-check
    if Path(rel).is_absolute():
        raise ValueError("Absolute paths are not allowed")
    p = (base / rel).resolve()
    _assert_under(base, p)
    return p


def _safe_open_read(path: Path, binary: bool = False) -> bytes | str:
    """
    Safely open and read a file, disallowing symlinks.
    """
    # Refuse symlinks; open with O_NOFOLLOW when supported
    st = os.lstat(path)
    if stat.S_ISLNK(st.st_mode):
        raise ValueError(f"Symlink not allowed: {path}")
    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    fd = os.open(path, flags)
    try:
        with os.fdopen(fd, "rb" if binary else "r") as f:
            return f.read()
    finally:
        try:
            os.close(fd)
        except OSError:
            pass


def _load_yaml_secure(base: Path, filename: str) -> dict:
    # Only accept a plain filename (no separators)
    if "/" in filename or "\\" in filename:
        raise ValueError("Config filename must not contain path separators")
    p = _safe_join(base, filename)
    data = _safe_open_read(p, binary=False)
    return yaml.safe_load(data) or {}


class CoordinatorService(pb_grpc.CoordinatorServicer):
    """
    Secure gRPC service for the MPC coordinator.
    """
    def __init__(self):
        self.parties = {}
        self.sessions = {}
        self.scheduler = AutoRegScheduler()

    def RegisterParty(self, request, context):
        attested = validate_attestation(b"placeholder")
        if not attested:
            return pb.RegisterAck(ok=False, msg="attestation failed")
        self.parties[request.party_id] = request.addr
        return pb.RegisterAck(ok=True, msg=f"Registered {request.party_id}")

    def CreateSession(self, request, context):
        self.sessions[request.session_id] = {
            "model": request.model_name,
            "ring": request.mpc_ring,
            "prompts": {},
        }
        self.scheduler.ensure_session(request.session_id)
        return pb.SessionAck(ok=True, msg="Session created")

    def SubmitPrompt(self, request, context):
        sess = self.sessions.get(request.session_id)
        if not sess:
            return pb.SubmitPromptAck(ok=False, msg="unknown session")
        sess["prompts"][request.owner_party] = request.token_ids
        self.scheduler.load_prompt_bytes(request.session_id, request.token_ids)
        return pb.SubmitPromptAck(ok=True, msg="Prompt received")

    def RunInference(self, request, context):
        for idx, (token_id, text, dt) in enumerate(
            self.scheduler.run(request.session_id,
                               request.max_new_tokens, topk=3)
        ):
            yield pb.InferenceEvent(token=pb.Token(token_id=token_id, text=text))
            yield pb.InferenceEvent(timing=pb.StepTiming(step_index=idx, ms=dt * 1000.0))

    def FetchMetrics(self, request, context):
        return pb.Metrics(tokens_per_second=0.0, triple_pool_remaining=0)


def serve(address="0.0.0.0:8080", metrics_port=9090):
    # Start Prometheus exporter
    start_http_server(metrics_port)

    # --- Load security config FROM FIXED LOCATION ---
    cfg = _load_yaml_secure(CONFIG_BASE, CFG_FILENAME)

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=8))

    # --- mTLS (certs confined to CERTS_BASE) ---
    tls_cfg = cfg.get("tls") or {}
    if tls_cfg.get("enabled", False):
        cert_path = _safe_join(
            CERTS_BASE, tls_cfg.get("server_cert", "server.crt"))
        key_path = _safe_join(CERTS_BASE, tls_cfg.get(
            "server_key",  "server.key"))
        # optional (None = server-auth only)
        ca_value = tls_cfg.get("client_ca")

        cert = _safe_open_read(cert_path, binary=True)
        key = _safe_open_read(key_path,  binary=True)

        if ca_value:
            ca_path = _safe_join(CERTS_BASE, ca_value)
            ca = _safe_open_read(ca_path, binary=True)
            creds = grpc.ssl_server_credentials(
                [(key, cert)], root_certificates=ca, require_client_auth=True
            )
        else:
            creds = grpc.ssl_server_credentials([(key, cert)])

        server.add_secure_port(address, creds)
        print("[coordinator] TLS/mTLS enabled")
    else:
        server.add_insecure_port(address)

    pb_grpc.add_CoordinatorServicer_to_server(CoordinatorService(), server)
    server.start()
    print(f"[coordinator] gRPC: {address} | /metrics: :{metrics_port}")
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        print("[coordinator] shutting down")


if __name__ == "__main__":
    serve()
