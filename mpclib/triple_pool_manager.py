
from typing import Dict, Tuple
from .triple_pool import TriplePool

class TriplePoolManager:
    def __init__(self):
        self.pools: Dict[Tuple[Tuple[int,int], Tuple[int,int]], TriplePool] = {}

    def get_pool(self, shapeA, shapeB, seed=0):
        key = (shapeA, shapeB)
        if key not in self.pools:
            self.pools[key] = TriplePool(shapeA, shapeB, seed=seed)
        return self.pools[key]

# Global
triple_pools = TriplePoolManager()
