
import numpy as np
from mpclib.fixed_point import FixedPoint

def test_roundtrip_and_ops():
    fp = FixedPoint(scale_bits=16)
    x = np.array([0.0, 0.5, -1.25, 3.14159], dtype=np.float64)
    enc = fp.encode(x)
    dec = fp.decode(enc)
    assert np.allclose(x, dec, atol=1e-3)

    y = np.array([1.0, -0.25, 2.0, -3.0], dtype=np.float64)
    a = fp.encode(x)
    b = fp.encode(y)

    add = fp.decode(fp.add(a, b))
    sub = fp.decode(fp.sub(a, b))
    mul = fp.decode(fp.mul(a, b))

    assert np.allclose(add, x + y, atol=1e-3)
    assert np.allclose(sub, x - y, atol=1e-3)
    assert np.allclose(mul, x * y, atol=1e-2)
