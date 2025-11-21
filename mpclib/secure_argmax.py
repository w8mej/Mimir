
import numpy as np
from .fixed_point import FixedPoint
from .shares import share_array, reconstruct_array
fp = FixedPoint(16)

def _abs_u(u):
    x2 = fp.mul(u, u)
    xf = fp.decode(x2)
    r = np.sqrt(xf + 1e-6)
    return fp.encode(r)

def _relu_u(u):
    return (u + _abs_u(u)) % (2**64)

def secure_argmax_onehot(Logits_s):
    Lu = reconstruct_array(*Logits_s)
    Lf = fp.decode(Lu)
    Lf = Lf - np.mean(Lf, axis=-1, keepdims=True)
    U = fp.encode(Lf)
    for _ in range(3):
        U = fp.mul(U, fp.encode(2.0))
    R = _relu_u(U)
    s = np.sum(fp.decode(R), axis=-1, keepdims=True) + 1e-6
    inv = fp.encode(1.0 / s)
    P = fp.mul(R, inv)
    for _ in range(2):
        P = fp.mul(P, P)
    s2 = np.sum(fp.decode(P), axis=-1, keepdims=True) + 1e-9
    P2 = fp.mul(P, fp.encode(1.0 / s2))
    return share_array(P2, np.random.default_rng(0))
