
import os, hmac, hashlib, numpy as np

class SplitCSPRNG:
    """
    Deterministic, splittable CSPRNG derived from a transcript hash.
    Each party would hold a distinct key; here we simulate by domain separation.
    """
    def __init__(self, root_key: bytes):
        self.root_key = root_key

    def derive(self, domain: str, step: int) -> np.random.Generator:
        msg = f"{domain}:{step}".encode()
        seed_bytes = hmac.new(self.root_key, msg, hashlib.sha256).digest()
        # convert to uint64 seed
        seed = int.from_bytes(seed_bytes[:8], 'big', signed=False)
        return np.random.default_rng(seed)
