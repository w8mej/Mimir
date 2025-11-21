
# Backward-compat shim that uses HMAC-DRBG with joint coin tossing
import os, numpy as np
from .hmac_drbg import HmacDrbg, joint_coin_toss_commit
class JointDRBG:
    def __init__(self, party_seeds=None):
        if party_seeds is None:
            party_seeds = [os.urandom(32), os.urandom(32), os.urandom(32)]
        seed, commits = joint_coin_toss_commit(party_seeds)
        self.drbg = HmacDrbg(seed)
    def derive(self, domain: str, step: int) -> np.random.Generator:
        return self.drbg.rng(domain, step)
