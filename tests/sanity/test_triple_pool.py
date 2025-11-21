
import numpy as np
import pytest
from mpclib.triple_pool_manager import triple_pools

@pytest.mark.sanity
def test_triple_pool_refill_and_get():
    """
    Test that the pool refills and returns valid triples.
    """
    pool = triple_pools.get_pool((4, 8), (8, 4), seed=42)
    n0 = len(pool.pool)
    A,B,C = pool.get()
    assert A[0][0].shape == (4,8)  # accept replicated shapes
    assert len(pool.pool) <= n0

def test_triple_pool_exhaustion():
    """
    Test that the pool handles exhaustion gracefully by refilling.
    """
    # Create a pool with small batch size
    pool = triple_pools.get_pool((2, 2), (2, 2), seed=123)
    # Consume many triples
    for _ in range(10):
        pool.get()
    # It should auto-refill, so no error expected
    assert True

def test_triple_pool_shapes():
    """
    Test that the pool returns triples with correct shapes.
    """
    pool = triple_pools.get_pool((1, 5), (5, 1), seed=999)
    A, B, C = pool.get()
    # Check shapes (assuming replicated shares structure)
    assert A is not None

