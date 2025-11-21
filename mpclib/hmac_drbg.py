
import hmac, hashlib, os, json, numpy as np
class HmacDrbg:
    # NIST SP 800-90A HMAC-DRBG (SHA-256)
    def __init__(self, seed_material: bytes):
        self.K = b"\x00"*32
        self.V = b"\x01"*32
        self._update(seed_material)
    def _hmac(self, key, data): return hmac.new(key, data, hashlib.sha256).digest()
    def _update(self, provided_data: bytes | None):
        self.K = self._hmac(self.K, self.V + b"\x00" + (provided_data or b""))
        self.V = self._hmac(self.K, self.V)
        if provided_data is not None and len(provided_data)>0:
            self.K = self._hmac(self.K, self.V + b"\x01" + provided_data)
            self.V = self._hmac(self.K, self.V)
    def reseed(self, seed_material: bytes): self._update(seed_material)
    def generate(self, nbytes=32):
        out=b""
        while len(out) < nbytes:
            self.V = self._hmac(self.K, self.V)
            out += self.V
        self._update(None)
        return out[:nbytes]
    def rng(self, domain: str, step: int) -> np.random.Generator:
        seed = int.from_bytes(self.generate(8), 'big', signed=False)
        return np.random.default_rng(seed)
def joint_coin_toss_commit(parties_entropy: list[bytes]) -> tuple[bytes, list[bytes]]:
    # Parties first publish commitments H(entropy), then reveal; we aggregate XOR to derive seed_material.
    commitments = [hashlib.sha256(e).digest() for e in parties_entropy]
    # In a real protocol, we'd verify these commitments asynchronously before reveal.
    seed_material = b"".join(sorted(parties_entropy))  # deterministic combine
    return hashlib.sha256(seed_material).digest(), commitments
