
import numpy as np
from prometheus_client import Counter, Gauge
from .triples import gen_beaver_triple_shared
from .triple_sacrifice import sacrifice_check

POOL_AVAILABLE = Gauge("mimir_triple_pool_available", "Available Beaver triples in pool")
POOL_SACRIFICED = Counter("mimir_triples_sacrificed_total", "Triples sacrificed for checks")

class TriplePool:
    """
    Manages a pool of Beaver triples for online phase efficiency.
    """
    def __init__(self, shapeA, shapeB, seed=0, min_size=4, target_size=16):
        """
        Initialize the triple pool.
        
        Args:
            shapeA: Shape of matrix A.
            shapeB: Shape of matrix B.
            seed: Random seed for generation.
            min_size: Minimum pool size before refill.
            target_size: Target pool size after refill.
        """
        self.shapeA = shapeA
        self.shapeB = shapeB
        self.rng = np.random.default_rng(seed)
        self.pool = []
        self.min_size = min_size
        self.target_size = target_size
        self._refill()
    def _refill(self):
        while len(self.pool) < self.target_size:
            A,B,C = gen_beaver_triple_shared(self.shapeA, self.shapeB, self.rng)
            self.pool.append((A,B,C))
        POOL_AVAILABLE.set(len(self.pool))
    def sacrifice(self, n=2) -> bool:
        """
        Sacrifice triples to check for correctness/malicious behavior.
        
        Args:
            n: Number of triples to sacrifice.
            
        Returns:
            True if check passes.
        """
        ok = True
        for _ in range(n):
            POOL_SACRIFICED.inc()
            ok = ok and sacrifice_check(self.shapeA, self.shapeB, self.rng)
        return ok
    def get(self):
        """
        Get a triple from the pool, refilling if necessary.
        
        Returns:
            A Beaver triple (A, B, C).
        """
        if len(self.pool) <= self.min_size:
            self._refill()
        return self.pool.pop()
