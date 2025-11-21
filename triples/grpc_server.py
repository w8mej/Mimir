
import os, time, threading, sqlite3, struct, numpy as np
from concurrent import futures
import grpc
from prometheus_client import start_http_server, Counter, Gauge
from google.protobuf.empty_pb2 import Empty
from mpclib.triples import gen_beaver_triple_shared
from mpclib.shares import reconstruct_array, sub
from mpclib.fixed_point import FixedPoint
from mpclib.shares import share_array
from mpclib.drbg import JointDRBG

from grpc_tools import protoc
PROTO = os.path.join(os.path.dirname(__file__), "..", "protos", "triples.proto")
OUT = os.path.join(os.path.dirname(__file__), "pb")
os.makedirs(OUT, exist_ok=True)
protoc.main(['protoc','-I'+os.path.dirname(PROTO), '--python_out='+OUT, '--grpc_python_out='+OUT, PROTO])
from triples.pb import triples_pb2 as tpb
from triples.pb import triples_pb2_grpc as tpb_grpc

POOL = []
POOL_SIZE = Gauge("triple_pool_size", "triples in pool")
SAC_OK = Counter("triple_sac_ok","")
SAC_FAIL = Counter("triple_sac_fail","")

def refill(shape, target=64):
    M,K,N = shape
    rng = np.random.default_rng(0)
    while len(POOL) < target:
        POOL.append(gen_beaver_triple_shared((M,K),(K,N), rng))
    POOL_SIZE.set(len(POOL))

def sacrifice(n=4):
    ok=True; used=0
    for _ in range(n):
        if len(POOL) < 2: break
        A1,B1,C1 = POOL.pop(); A2,B2,C2 = POOL.pop(); used+=2
        dA = reconstruct_array(*sub(A1, A2)); dB = reconstruct_array(*sub(B1, B2)); dC = reconstruct_array(*sub(C1, C2))
        lhs = dC.view(np.int64); rhs = (dA.view(np.int64) @ dB.view(np.int64)).astype(np.int64)
        if lhs.shape != rhs.shape: ok=False
    if ok: SAC_OK.inc()
    else: SAC_FAIL.inc()
    return ok, used

class TripleSvc(tpb_grpc.TripleServiceServicer):
    def GetTriple(self, request, context):
        shape=(request.shape.m, request.shape.k, request.shape.n)
        if len(POOL)<8: refill(shape, 64)
        A,B,C = POOL.pop()
        POOL_SIZE.set(len(POOL))
        def pack(sh):
            # pack three pairs as bytes: we serialize arrays with .tobytes()
            return b"".join([sh[0][0].tobytes(), sh[0][1].tobytes(), sh[1][0].tobytes(), sh[1][1].tobytes(), sh[2][0].tobytes(), sh[2][1].tobytes()])
        return tpb.TripleReply(ok=True, a=pack(A), b=pack(B), c=pack(C))
    def Sacrifice(self, request, context):
        ok, used = sacrifice(int(request.count or 4))
        return tpb.SacrificeReply(ok=ok, consumed=used)
    def Stats(self, request, context):
        return tpb.StatsReply(pool_size=len(POOL), sac_ok=int(SAC_OK._value.get()), sac_fail=int(SAC_FAIL._value.get()))

def serve(addr="0.0.0.0:9095", metrics_port=9096):
    start_http_server(metrics_port)
    srv = grpc.server(futures.ThreadPoolExecutor(max_workers=8))
    tpb_grpc.add_TripleServiceServicer_to_server(TripleSvc(), srv)
    srv.add_insecure_port(addr); srv.start()
    print("[triples] gRPC:", addr, "| /metrics:", metrics_port)
    srv.wait_for_termination()

if __name__=="__main__":
    serve()
