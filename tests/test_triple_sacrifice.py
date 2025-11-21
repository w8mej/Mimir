import numpy as np
from mpclib.triple_sacrifice import sacrifice_check

def test_sacrifice_check_valid():
    rng = np.random.default_rng(123)
    # Shapes for matrix multiplication (m, k) @ (k, n) -> (m, n)
    shapeA = (4, 5)
    shapeB = (5, 3)
    
    # The sacrifice check generates valid triples internally and checks them
    # So it should return True
    assert sacrifice_check(shapeA, shapeB, rng)

def test_sacrifice_check_determinism():
    rng1 = np.random.default_rng(123)
    rng2 = np.random.default_rng(123)
    shapeA = (2, 2)
    shapeB = (2, 2)
    
    # Should be deterministic with same RNG state
    assert sacrifice_check(shapeA, shapeB, rng1) == sacrifice_check(shapeA, shapeB, rng2)
