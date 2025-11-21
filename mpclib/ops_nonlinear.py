
import numpy as np
from .fixed_point import FixedPoint
from .shares import reconstruct_array, share_array

RING = 2**64
fp = FixedPoint(scale_bits=16)

def open_value(Xs):
    return reconstruct_array(*Xs)

def gelu_poly_shares(Xs):
    X = open_value(Xs)
    x2 = fp.mul(X, X)
    x3 = fp.mul(x2, X)
    half = fp.encode(0.5)
    c3 = fp.encode(0.0356774)
    t1 = fp.mul(half, X)
    t2 = fp.mul(c3, x3)
    y = (t1 + t2) % RING
    return share_array(y, np.random.default_rng(0))

def softmax_clip_shares(Logits_s, clip_min=-6.0, clip_max=6.0):
    L = open_value(Logits_s)
    Lf = fp.decode(L)
    Lf = np.clip(Lf, clip_min, clip_max)
    z = fp.encode(Lf)
    z2 = fp.mul(z, z)
    z3 = fp.mul(z2, z)
    one = fp.encode(1.0)
    half = fp.encode(0.5)
    one_sixth = fp.encode(1.0/6.0)
    expz = (one + z + fp.mul(half, z2) + fp.mul(one_sixth, z3)) % RING
    sum_expz_u = np.sum(expz, axis=-1, keepdims=True, dtype=np.uint64) % RING
    sum_expz = fp.decode(sum_expz_u)
    inv = 1.0 / sum_expz
    inv_u = fp.encode(inv)
    probs = fp.mul(expz, inv_u)
    return share_array(probs, np.random.default_rng(0))

def rmsnorm_shares_open(Xs, eps=1e-5):
    """
    RMSNorm approximation: y = x / sqrt(mean(x^2) + eps)
    For MVP we open per-row norm only, then re-share.
    """
    X = open_value(Xs)
    Xf = fp.decode(X)
    rms = np.sqrt(np.mean(Xf*Xf, axis=-1, keepdims=True) + eps)
    inv = 1.0 / rms
    inv_u = fp.encode(inv)
    Y = fp.mul(X, inv_u)
    return share_array(Y, np.random.default_rng(0))

def topk_sample_open(Probs_s, k=3, seed=0):
    """
    Open probabilities, take top-k, sample with PRNG for determinism.
    Returns sampled index per row (public int).
    """
    P = open_value(Probs_s)
    Pf = fp.decode(P)
    rng = np.random.default_rng(seed)
    out = []
    for row in Pf:
        idx = np.argpartition(-row, k)[:k]
        w = row[idx]
        w = np.maximum(w, 1e-12)
        w = w / np.sum(w)
        choice = rng.choice(idx, p=w)
        out.append(int(choice))
    return out
