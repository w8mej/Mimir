
import numpy as np
from mpclib.shares import share_array, reconstruct_array
from mpclib.fixed_point import FixedPoint
from mpclib.ops_attn import self_attention_shares

def test_attention_shapes():
    rng = np.random.default_rng(0)
    fp = FixedPoint(16)
    T, d = 4, 8
    X = rng.normal(size=(T,d)).astype(np.float64)
    Xu = fp.encode(X)
    Xs = share_array(Xu, rng)

    def randW(m, n):
        return fp.encode(rng.normal(scale=0.02, size=(m,n)).astype(np.float64))

    Wq = share_array(randW(d,d), rng)
    Wk = share_array(randW(d,d), rng)
    Wv = share_array(randW(d,d), rng)
    Wo = share_array(randW(d,d), rng)

    Ys = self_attention_shares(Xs, Wq, Wk, Wv, Wo, scale=1.0/np.sqrt(d))
    Yu = reconstruct_array(*Ys)
    assert Yu.shape == (T, d)
