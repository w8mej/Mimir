
import json, os, numpy as np
from .fixed_point import FixedPoint
fp = FixedPoint(16)
# Load coefficients if present, else fallback to baked defaults
_DEFAULT = [65536, 65538, 32769, 10922, 2731, 546, 91]  # rough defaults scaled by 2^16
COEFF_FIXED = None
PATH = os.path.join(os.path.dirname(__file__), "..", "configs", "cheby_exp_deg6.json")
try:
    with open(PATH, "r") as f:
        data = json.load(f); COEFF_FIXED = data["coeff_fixed"]
except Exception:
    COEFF_FIXED = _DEFAULT

def cheby_exp_fixed(u_fixed):
    # Horner with fixed-point mul
    acc = np.uint64(COEFF_FIXED[-1])
    for c in reversed(COEFF_FIXED[:-1]):
        acc = fp.mul(acc, u_fixed)
        acc = (acc + np.uint64(c)) % (2**64)
    return acc
