
import numpy as np
from mpclib.fixed_point import FixedPoint
from mpclib.shares import share_array, reconstruct_array
from mpclib.ops_linear import beaver_matmul
from mpclib.triples import gen_beaver_triple

def test_secure_matmul_fixedpoint():
    rng = np.random.default_rng(1)
    fp = FixedPoint(scale_bits=16)
    m,k,n = 3,4,5
    Xf = rng.normal(size=(m,k)).astype(np.float64)
    Wf = rng.normal(size=(k,n)).astype(np.float64)

    Xu = fp.encode(Xf)
    Wu = fp.encode(Wf)

    # share X and W
    P0x, P1x, P2x = share_array(Xu, rng)
    P0w, P1w, P2w = share_array(Wu, rng)

    # triple
    A,B,C = gen_beaver_triple((m,k),(k,n), rng)

    # secure matmul
    Zshares = beaver_matmul((P0x,P1x,P2x), (P0w,P1w,P2w), (A,B,C))
    Zu = reconstruct_array(*Zshares)
    Zf = fp.decode(Zu)

    ref = Xf @ Wf
    assert np.allclose(Zf, ref, atol=5e-2)  # allow approximation error from fixed-point
