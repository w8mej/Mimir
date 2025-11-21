
from typing import Optional
from .shares import reconstruct_array
from .mac_manager import default_mac_manager as _mm

def open_with_mac_named(name: Optional[str], Xs):
    val = reconstruct_array(*Xs)
    if name is not None:
        ok = _mm.verify_open(name, Xs, val)
        if not ok:
            raise ValueError(f"MAC verification failed on open: {name}")
    return val
