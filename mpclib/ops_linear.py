
import numpy as np
from .shares import add, sub, mul_public, reconstruct_array, share_array
from .maced_shares import MacContext, macify, check_open

def beaver_matmul_shared(Xs, Ys, triple_shared, mac_ctx: MacContext):
    A,B,C = triple_shared
    d_sh = sub(Xs, A)
    e_sh = sub(Ys, B)
    d_mac = macify(d_sh, mac_ctx)
    e_mac = macify(e_sh, mac_ctx)
    d = reconstruct_array(*d_sh); e = reconstruct_array(*e_sh)
    assert check_open(d, d_sh, d_mac, mac_ctx)
    assert check_open(e, e_sh, e_mac, mac_ctx)
    term1 = mul_public(B, d.astype(np.uint64))
    term2 = mul_public(A, e.astype(np.uint64))
    de = (d.astype(np.int64) @ e.astype(np.int64)).astype(np.uint64)
    de_s = share_array(de, np.random.default_rng(0))
    tmp = add(C, term1); tmp = add(tmp, term2); Zs = add(tmp, de_s)
    return Zs

def linear_layer(Xs, W_s, triple_shared, mac_ctx: MacContext):
    return beaver_matmul_shared(Xs, W_s, triple_shared, mac_ctx)
