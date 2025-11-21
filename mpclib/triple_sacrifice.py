
import numpy as np
from .triples import gen_beaver_triple_shared
from .shares import reconstruct_array

def sacrifice_check(shapeA, shapeB, rng) -> bool:
    """
    Generate two triples and check their relation on random masks (simplified sacrifice).
    """
    A1,B1,C1 = gen_beaver_triple_shared(shapeA, shapeB, rng)
    A2,B2,C2 = gen_beaver_triple_shared(shapeA, shapeB, rng)
    # Open (A1 - A2), (B1 - B2) to ensure C1 - C2 == (A1-A2)@(B1-B2)
    from .shares import sub_shares
    dA = reconstruct_array(*sub_shares(A1, A2))
    dB = reconstruct_array(*sub_shares(B1, B2))
    dC = reconstruct_array(*sub_shares(C1, C2))

    lhs = dC.view(np.int64)
    rhs = (dA.view(np.int64) @ dB.view(np.int64)).astype(np.int64)
    return np.array_equal(lhs, rhs)
