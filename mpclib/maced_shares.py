
import numpy as np
R = 2**64
class MacContext:
    """
    Context for MAC operations, holding the global key alpha.
    """
    def __init__(self, alpha: np.uint64): self.alpha = np.uint64(alpha)
def reconstruct_pair(pair): return (pair[0].astype(np.int64)+pair[1].astype(np.int64)) % (2**64)
def macify(shares, mac_ctx: MacContext):
    """
    Compute MACs for the given shares.
    
    Args:
        shares: The replicated shares to MAC.
        mac_ctx: The MAC context containing the key.
        
    Returns:
        A tuple of MAC shares.
    """
    def mac_pair(pair):
        x = reconstruct_pair(pair)
        tau = (x.astype(np.int64)*mac_ctx.alpha.astype(np.int64))%(2**64)
        rng = np.random.default_rng(0)
        m0 = rng.integers(0, 2**64, size=x.shape, dtype=np.uint64)
        m1 = rng.integers(0, 2**64, size=x.shape, dtype=np.uint64)
        m2 = (tau.astype(np.uint64) - m0 - m1) % R
        return ((m0, m1), (m1, m2), (m2, m0))
    return (mac_pair(shares[0]), mac_pair(shares[1]), mac_pair(shares[2]))
def check_open(opened_u, shares, mac_shares, mac_ctx: MacContext) -> bool:
    def rec(pair): return (pair[0].astype(np.int64)+pair[1].astype(np.int64))%(2**64)
    m = (rec(mac_shares[0]) + rec(mac_shares[1]) + rec(mac_shares[2]))%(2**64)
    expect = (opened_u.view(np.int64)*mac_ctx.alpha.astype(np.int64))%(2**64)
    return np.array_equal(expect.astype(np.uint64), m.astype(np.uint64))
