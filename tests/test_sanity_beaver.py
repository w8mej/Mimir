
import numpy as np, pytest
from mpclib.fixed_point import FixedPoint
from mpclib.shares import share_array, reconstruct_array
from mpclib.triples import gen_beaver_triple_shared
from mpclib.ops_linear import beaver_matmul_shared
from mpclib.maced_shares import MacContext
fp = FixedPoint(16)
@pytest.mark.sanity
def test_beaver():
    rng = np.random.default_rng(0)
    Xf = rng.normal(size=(2,3)).astype(np.float64); Yf = rng.normal(size=(3,4)).astype(np.float64)
    Xu=fp.encode(Xf); Yu=fp.encode(Yf); Xs=share_array(Xu, rng); Ys=share_array(Yu, rng)
    A,B,C=gen_beaver_triple_shared((2,3),(3,4), rng); mac=MacContext(np.uint64(0x9E3779B185EBCA87))
    Zs = beaver_matmul_shared(Xs, Ys, (A,B,C), mac); from mpclib.shares import reconstruct_array
    Zf = fp.decode(reconstruct_array(*Zs)); assert Zf.shape==(2,4)
