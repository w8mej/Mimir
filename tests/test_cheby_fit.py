
import json, os, numpy as np, pytest
from mpclib.fixed_point import FixedPoint
from mpclib.cheby import cheby_exp_fixed
fp = FixedPoint(16)
@pytest.mark.sanity
def test_cheby_fixed_reasonable():
    xs = np.linspace(-6,6,201)
    xq = fp.encode(xs)
    y = np.exp(xs)
    y_hat = fp.decode(cheby_exp_fixed(xq))
    assert np.max(np.abs(y - y_hat)) < 0.1
