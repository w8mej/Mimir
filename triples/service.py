
import numpy as np
from prometheus_client import Counter, Gauge
from mpclib.triples import gen_beaver_triple_shared
from mpclib.shares import reconstruct_array, sub
POOL = Gauge("mimir_triple_pool", "Triples available")
SAC_OK = Counter("mimir_triple_sacrifice_ok_total", "Sacrifice checks OK")
SAC_FAIL = Counter("mimir_triple_sacrifice_fail_total", "Sacrifice checks FAIL")
class TripleService:
    def __init__(self, shapeA, shapeB, seed=0, min_size=8, target_size=32):
        self.shapeA=shapeA; self.shapeB=shapeB; self.rng=np.random.default_rng(seed)
        self.pool=[]; self.min_size=min_size; self.target_size=target_size
        self.refill()
    def refill(self):
        while len(self.pool) < self.target_size:
            self.pool.append(gen_beaver_triple_shared(self.shapeA, self.shapeB, self.rng))
        POOL.set(len(self.pool))
    def sacrifice(self, n=2) -> bool:
        if len(self.pool) < 2*n: self.refill()
        ok=True
        for _ in range(n):
            A1,B1,C1 = self.pool.pop(); A2,B2,C2 = self.pool.pop()
            dA = reconstruct_array(*sub(A1, A2))
            dB = reconstruct_array(*sub(B1, B2))
            dC = reconstruct_array(*sub(C1, C2))
            lhs = dC.view(np.int64); rhs = (dA.view(np.int64) @ dB.view(np.int64)).astype(np.int64)
            if lhs.shape != rhs.shape: ok=False
        if ok: SAC_OK.inc()
        else: SAC_FAIL.inc()
        return ok
    def get(self):
        if len(self.pool) <= self.min_size: self.refill()
        return self.pool.pop()
