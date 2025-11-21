
import numpy as np
from .fixed_point import FixedPoint
from .shares import share_array, reconstruct_array, mul_public
from .maced_shares import MacContext, macify, check_open
from .cheby import cheby_exp_fixed
RING = 2**64
fp = FixedPoint(16)

def secure_softmax_cheby(Logits_s, drbg, step: int, mac_ctx: MacContext, clip=6.0):
    # Masked LSE style: center via row max (kept secret), reveal *only* masked sums with MAC.
    L = reconstruct_array(*Logits_s)
    Lf = fp.decode(L)
    Lf = np.clip(Lf - np.max(Lf, axis=-1, keepdims=True), -clip, clip)  # public centering value only as constant 'clip'
    Z = fp.encode(Lf)
    Ez = cheby_exp_fixed(Z)                      # stays secret until re-shared
    Ez_s = share_array(Ez, drbg.derive("expz", step))
    s = Ez.sum(axis=-1, keepdims=True).astype(np.uint64)     # sum is deterministic; we open it with MAC
    Sum_s = ((s, s*0), (s, s*0), (s, s*0))
    Sum_mac = macify(Sum_s, mac_ctx)
    su = reconstruct_array(*Sum_s)
    assert check_open(su, Sum_s, Sum_mac, mac_ctx), "MAC fail on softmax sum"
    inv = 1.0 / np.clip(su.astype(np.float64) / float(1<<16), 1e-12, None)
    inv_u = fp.encode(inv)
    probs_u = fp.mul(Ez, inv_u)
    Probs_s = share_array(probs_u, drbg.derive("probs", step))
    return Probs_s
