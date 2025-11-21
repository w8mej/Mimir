
import numpy as np
import pytest
from mpclib.fixed_point import FixedPoint
from mpclib.shares import share_array, reconstruct_array
from mpclib.secure_softmax import secure_softmax
from mpclib.drbg import JointDRBG

fp = FixedPoint(16)

@pytest.mark.sanity
def test_secure_softmax_mac_open_sum():
    rng = np.random.default_rng(0)
    L = rng.normal(size=(2,5)).astype(np.float64)
    L = fp.encode(L)
    Xs = share_array(L, rng)
    prng = JointDRBG()
    P = secure_softmax(Xs, prng, step=1)
    Pu = reconstruct_array(*P)
    Pf = fp.decode(Pu)
    assert np.allclose(Pf.sum(axis=-1), 1.0, atol=1e-2)
