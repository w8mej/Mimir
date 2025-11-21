import numpy as np
import pytest
from mpclib.csprng import SplitCSPRNG

def test_csprng_determinism():
    root_key = b'secret_key'
    csprng1 = SplitCSPRNG(root_key)
    csprng2 = SplitCSPRNG(root_key)
    
    rng1 = csprng1.derive("test_domain", 0)
    rng2 = csprng2.derive("test_domain", 0)
    
    assert rng1.random() == rng2.random()

def test_csprng_domain_separation():
    root_key = b'secret_key'
    csprng = SplitCSPRNG(root_key)
    
    rng1 = csprng.derive("domain1", 0)
    rng2 = csprng.derive("domain2", 0)
    
    assert rng1.random() != rng2.random()

def test_csprng_step_separation():
    root_key = b'secret_key'
    csprng = SplitCSPRNG(root_key)
    
    rng1 = csprng.derive("domain", 0)
    rng2 = csprng.derive("domain", 1)
    
    assert rng1.random() != rng2.random()
