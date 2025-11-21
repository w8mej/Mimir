
import numpy as np
from mpclib.triples import gen_beaver_triple

def test_beaver_triple_correctness():
    rng = np.random.default_rng(7)
    m, k, n = 4, 5, 3
    A, B, C = gen_beaver_triple((m, k), (k, n), rng)

    A_s = A.view(np.int64)
    B_s = B.view(np.int64)
    C_s = C.view(np.int64)
    prod = (A_s @ B_s).astype(np.int64)
    assert np.array_equal(prod.astype(np.uint64), C)
