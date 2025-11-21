
import numpy as np
R64 = 2**64
class FixedPoint:
    def __init__(self, scale_bits=16):
        self.scale_bits = scale_bits
        self.S = np.float64(1<<scale_bits)
    def encode(self, x):
        return np.array(np.round(np.array(x, dtype=np.float64)*self.S), dtype=np.uint64)
    def decode(self, u):
        return np.array(u, dtype=np.float64)/self.S
    def mul(self, a, b):
        ai = a.astype(np.int64); bi = b.astype(np.int64)
        prod = (ai*bi) >> self.scale_bits
        return prod.astype(np.uint64)
