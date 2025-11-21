
import numpy as np
from .ops_linear import linear_layer, beaver_matmul_shared
from .secure_softmax import secure_softmax_cheby
from .shares import reconstruct_array, transpose_shares, mul_public, share_array
from .fixed_point import FixedPoint
from .triples import gen_beaver_triple_shared
from .drbg import JointDRBG
from .maced_shares import MacContext
fp = FixedPoint(scale_bits=16)
class SharedKVCache:
    def __init__(self): self.data = {}
    def append(self, layer_id, K_s, V_s):
        rec = self.data.get(layer_id, {"K": None, "V": None})
        if rec["K"] is None: rec["K"]=K_s; rec["V"]=V_s
        else:
            def cat(a,b): return (np.concatenate([a[0], b[0]], axis=0), np.concatenate([a[1], b[1]], axis=0))
            rec["K"]=(cat(rec["K"][0],K_s[0]),cat(rec["K"][1],K_s[1]),cat(rec["K"][2],K_s[2]))
            rec["V"]=(cat(rec["V"][0],V_s[0]),cat(rec["V"][1],V_s[1]),cat(rec["V"][2],V_s[2]))
        self.data[layer_id] = rec
    def get(self, layer_id): return self.data.get(layer_id, {"K": None, "V": None})
def self_attention_shares(Xs, Wq_s, Wk_s, Wv_s, Wo_s, scale=None, kv: SharedKVCache=None, layer_id=0, drbg: JointDRBG | None=None, step:int=0, mac_ctx: MacContext | None=None):
    if mac_ctx is None: import numpy as np; mac_ctx = MacContext(np.uint64(0x9E3779B185EBCA87))
    T, d_model = reconstruct_array(*Xs).shape
    d_k = d_model
    def triple(shapeA, shapeB, seed):
        rng = np.random.default_rng(seed)
        return gen_beaver_triple_shared(shapeA, shapeB, rng)
    A1,B1,C1 = triple((T,d_model),(d_model,d_k), step*31+1); Qs = linear_layer(Xs, Wq_s, (A1,B1,C1), mac_ctx)
    A2,B2,C2 = triple((T,d_model),(d_model,d_k), step*31+2); Ks_new = linear_layer(Xs, Wk_s, (A2,B2,C2), mac_ctx)
    A3,B3,C3 = triple((T,d_model),(d_model,d_k), step*31+3); Vs_new = linear_layer(Xs, Wv_s, (A3,B3,C3), mac_ctx)
    if kv is not None:
        prev = kv.get(layer_id)
        if prev["K"] is not None:
            def cat(a,b): return (np.concatenate([a[0], b[0]], axis=0), np.concatenate([a[1], b[1]], axis=0))
            Ks = (cat(prev["K"][0], Ks_new[0]), cat(prev["K"][1], Ks_new[1]), cat(prev["K"][2], Ks_new[2]))
            Vs = (cat(prev["V"][0], Vs_new[0]), cat(prev["V"][1], Vs_new[1]), cat(prev["V"][2], Vs_new[2]))
        else: Ks, Vs = Ks_new, Vs_new
        kv.append(layer_id, Ks_new, Vs_new)
    else: Ks, Vs = Ks_new, Vs_new
    Kt = transpose_shares(Ks)
    A4,B4,C4 = triple((T,d_k),(d_k, reconstruct_array(*Ks).shape[0]), step*31+4)
    Scores_s = beaver_matmul_shared(Qs, Kt, (A4,B4,C4), mac_ctx)
    if scale is not None:
        scale_u = fp.encode(scale); Scores_s = mul_public(Scores_s, scale_u)
    if drbg is None: drbg = JointDRBG()
    Attn_s = secure_softmax_cheby(Scores_s, drbg, step, mac_ctx=mac_ctx)
    A5,B5,C5 = triple((T, reconstruct_array(*Attn_s).shape[1]), (reconstruct_array(*Vs).shape[0], d_k), step*31+5)
    Cs = beaver_matmul_shared(Attn_s, Vs, (A5,B5,C5), mac_ctx)
    A6,B6,C6 = triple((T,d_k),(d_k,d_model), step*31+6)
    Ys = linear_layer(Cs, Wo_s, (A6,B6,C6), mac_ctx)
    return Ys
