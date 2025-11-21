
import numpy as np
from mpclib.shares import share_scalar, reconstruct_scalar

def test_share_and_reconstruct_many():
    rng = np.random.default_rng(123)
    for _ in range(100):
        x = np.uint64(rng.integers(0, 2**64, dtype=np.uint64))
        p0, p1, p2 = share_scalar(x, rng)
        xr = reconstruct_scalar(p0, p1, p2)
        assert xr == x
