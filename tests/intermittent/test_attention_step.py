
import numpy as np
import pytest
from mpclib.fixed_point import FixedPoint
from mpclib.shares import share_array, reconstruct_array
from mpclib.ops_attn import self_attention_shares, SharedKVCache
from mpclib.triples import gen_beaver_triple_shared

fp = FixedPoint(16)

@pytest.mark.intermittent
def test_attention_step_shapes():
    rng = np.random.default_rng(0)
    T, d = 3, 8
    X = rng.normal(size=(T,d)).astype(np.float64)
    Xu = fp.encode(X)
    Xs = share_array(Xu, rng)

    def randW(m, n):
        return share_array(fp.encode(rng.normal(scale=0.02, size=(m,n))), rng)

    Wq=Wk=Wv=Wo=randW(d,d)
    kv = SharedKVCache()
    Y = self_attention_shares(Xs, Wq, Wk, Wv, Wo, scale=1.0/np.sqrt(d), kv=kv, step=0)
    Yu = reconstruct_array(*Y)
    assert Yu.shape == (T, d)
