import pytest
import numpy as np
from mpclib.hmac_drbg import HmacDrbg

def test_hmac_drbg_determinism():
    seed = b"test_seed"
    drbg1 = HmacDrbg(seed)
    drbg2 = HmacDrbg(seed)
    assert drbg1.generate(32) == drbg2.generate(32)

def test_hmac_drbg_distinct():
    drbg1 = HmacDrbg(b"seed1")
    drbg2 = HmacDrbg(b"seed2")
    assert drbg1.generate(32) != drbg2.generate(32)

def test_hmac_drbg_reseed():
    drbg = HmacDrbg(b"seed")
    out1 = drbg.generate(32)
    drbg.reseed(b"additional")
    out2 = drbg.generate(32)
    assert out1 != out2

def test_rng_output():
    drbg = HmacDrbg(b"seed")
    rng = drbg.rng("domain", 0)
    assert isinstance(rng, np.random.Generator)
    val1 = rng.random()
    
    drbg2 = HmacDrbg(b"seed")
    rng2 = drbg2.rng("domain", 0)
    assert val1 == rng2.random()
