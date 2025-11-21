
import numpy as np
R = 2**64
def share_array(U, rng):
    """
    Secret-share an array U into three replicated shares using the given RNG.
    
    Args:
        U: The array to share.
        rng: The random number generator to use.
        
    Returns:
        A tuple of three shares ((a,b), (b,c), (c,a)).
    """
    a = rng.integers(0, 2**64, size=U.shape, dtype=np.uint64)
    b = rng.integers(0, 2**64, size=U.shape, dtype=np.uint64)
    c = (U - a - b) % R
    return ( (a,b), (b,c), (c,a) )
def reconstruct_array(p0, p1, p2):
    """
    Reconstruct an array from three replicated shares.
    
    Args:
        p0, p1, p2: The three shares held by the parties.
        
    Returns:
        The reconstructed array.
    """
    (a,b)=p0; (b2,c)=p1; (c2,a2)=p2
    x = (a.astype(np.int64)+b.astype(np.int64)+c.astype(np.int64)) % (2**64)
    return x.astype(np.uint64)
def add(A, B):
    def ap(pa, pb): return ((pa[0]+pb[0])%R, (pa[1]+pb[1])%R)
    return (ap(A[0],B[0]), ap(A[1],B[1]), ap(A[2],B[2]))
def sub(A, B):
    def sp(pa, pb): return ((pa[0]-pb[0])%R, (pa[1]-pb[1])%R)
    return (sp(A[0],B[0]), sp(A[1],B[1]), sp(A[2],B[2]))
def add_public(A, u):
    def ap(pa): return ((pa[0]+u)%R, pa[1])
    return (ap(A[0]), ap(A[1]), ap(A[2]))
def mul_public(A, u):
    def mp(pa):
        return ((pa[0].astype(np.int64)*u.astype(np.int64))%(2**64)).astype(np.uint64),                ((pa[1].astype(np.int64)*u.astype(np.int64))%(2**64)).astype(np.uint64)
    return (mp(A[0]), mp(A[1]), mp(A[2]))
def transpose_shares(S):
    def t(p): return (p[0].T, p[1].T)
    return (t(S[0]), t(S[1]), t(S[2]))
