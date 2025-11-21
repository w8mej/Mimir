
import numpy as np
from mpclib.fixed_point import FixedPoint
from mpclib.shares import share_array, reconstruct_array
from mpclib.ops_linear import linear_layer, beaver_matmul_shared
from mpclib.ops_attn import self_attention_shares, SharedKVCache
from mpclib.triples import gen_beaver_triple_shared
from mpclib.drbg import JointDRBG
from mpclib.maced_shares import MacContext
fp = FixedPoint(scale_bits=16)
class TinyTransformer2L:
    def __init__(self, d_model=32, d_ff=64, vocab_size=256, seed=0):
        self.d_model = d_model; self.d_ff=d_ff; self.vocab_size=vocab_size
        self.rng = np.random.default_rng(seed); self.kv = SharedKVCache(); self.drbg = JointDRBG()
        self.mac = MacContext(np.uint64(0x9E3779B185EBCA87))
        def rand_mat(m,n): return self.rng.normal(scale=0.02,size=(m,n)).astype(np.float64)
        self.E = rand_mat(vocab_size, d_model)
        self.Wq0=rand_mat(d_model,d_model); self.Wk0=rand_mat(d_model,d_model); self.Wv0=rand_mat(d_model,d_model); self.Wo0=rand_mat(d_model,d_model)
        self.Wq1=rand_mat(d_model,d_model); self.Wk1=rand_mat(d_model,d_model); self.Wv1=rand_mat(d_model,d_model); self.Wo1=rand_mat(d_model,d_model)
        self.Wo=rand_mat(d_model, vocab_size)
    def encode_params(self):
        def enc(M):
            Mu=fp.encode(M); import numpy as np; from mpclib.shares import share_array
            return share_array(Mu, np.random.default_rng(123))
        self.E_s=enc(self.E)
        self.Wq0_s=enc(self.Wq0); self.Wk0_s=enc(self.Wk0); self.Wv0_s=enc(self.Wv0); self.Wo0_s=enc(self.Wo0)
        self.Wq1_s=enc(self.Wq1); self.Wk1_s=enc(self.Wk1); self.Wv1_s=enc(self.Wv1); self.Wo1_s=enc(self.Wo1)
        self.Wo_s=enc(self.Wo)
    def embed_tokens(self, token_ids):
        T=len(token_ids); one_hot=np.zeros((T,self.vocab_size),dtype=np.float64)
        for t,idx in enumerate(token_ids): one_hot[t,int(idx)%self.vocab_size]=1.0
        one_hot_u=fp.encode(one_hot); P0,P1,P2=share_array(one_hot_u, np.random.default_rng(0))
        A,B,C=gen_beaver_triple_shared((T,self.vocab_size),(self.vocab_size,self.d_model), np.random.default_rng(0))
        Zs=beaver_matmul_shared((P0,P1,P2), self.E_s,(A,B,C), self.mac)
        return Zs
    def forward_step(self, token_ids, step):
        if not hasattr(self,"E_s"): self.encode_params()
        Xs=self.embed_tokens(token_ids[-1:]); scale=1.0/np.sqrt(self.d_model)
        Xs=self_attention_shares(Xs,self.Wq0_s,self.Wk0_s,self.Wv0_s,self.Wo0_s,scale=scale,kv=self.kv,layer_id=0,drbg=self.drbg,step=step, mac_ctx=self.mac)
        Xs=self_attention_shares(Xs,self.Wq1_s,self.Wk1_s,self.Wv1_s,self.Wo1_s,scale=scale,kv=self.kv,layer_id=1,drbg=self.drbg,step=step, mac_ctx=self.mac)
        A,B,C=gen_beaver_triple_shared((Xs[0][0].shape[1], self.Wo_s[0][0].shape[0]), (self.Wo_s[0][0].shape[0], self.Wo_s[0][0].shape[1]), np.random.default_rng(9))
        Ls=linear_layer(Xs, self.Wo_s, (A,B,C), self.mac); return Ls
    def next_token_secure_index(self, token_ids):
        step=len(token_ids); Ls=self.forward_step(token_ids, step)
        from mpclib.shares import reconstruct_array
        Lu=reconstruct_array(*Ls); Lf=fp.decode(Lu); j=int(np.argmax(Lf[-1])); return j
