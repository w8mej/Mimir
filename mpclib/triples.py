
import numpy as np
from .shares import share_array
def gen_beaver_triple_shared(shapeA, shapeB, rng):
    A = rng.integers(0, 2**16, size=shapeA, dtype=np.uint64)
    B = rng.integers(0, 2**16, size=shapeB, dtype=np.uint64)
    C = (A.astype(np.int64) @ B.astype(np.int64)).astype(np.uint64)
    return share_array(A, rng), share_array(B, rng), share_array(C, rng)
