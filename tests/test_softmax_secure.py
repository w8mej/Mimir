
import numpy as np
from mpclib.fixed_point import FixedPoint
from mpclib.shares import share_array, reconstruct_array
from mpclib.ops_nonlinear import softmax_clip_shares, gelu_poly_shares

def softmax_float(x):
    x = x - np.max(x, axis=-1, keepdims=True)
    e = np.exp(x)
    return e / np.sum(e, axis=-1, keepdims=True)

def test_softmax_clip():
    rng = np.random.default_rng(0)
    fp = FixedPoint(scale_bits=16)
    x = rng.normal(size=(2,6)).astype(np.float64)
    xu = fp.encode(x)

    Xs = share_array(xu, rng)
    Ps = softmax_clip_shares(Xs, -6.0, 6.0)
    Pu = reconstruct_array(*Ps)
    Pf = fp.decode(Pu)

    ref = softmax_float(np.clip(x, -6, 6))
    assert np.allclose(Pf, ref, atol=5e-2)
    # rows sum to ~1
    s = np.sum(Pf, axis=-1)
    assert np.allclose(s, np.ones_like(s), atol=5e-2)

def test_gelu_poly():
    rng = np.random.default_rng(0)
    fp = FixedPoint(scale_bits=16)
    x = rng.normal(size=(8,)).astype(np.float64)
    xu = fp.encode(x)
    Xs = share_array(xu, rng)

    Ys = gelu_poly_shares(Xs)
    Yu = reconstruct_array(*Ys)
    Yf = fp.decode(Yu)

    # reference using tanh formulation (float), not polynomial
    ref = 0.5*x*(1.0 + np.tanh(np.sqrt(2/np.pi)*(x + 0.044715*x**3)))
    # check coarse approximation
    assert np.allclose(Yf, ref, atol=1.0)  # loose tolerance; it's a cubic fit
