
#!/usr/bin/env python3
import re
import os
from pathlib import Path
import numpy as np
import argparse
import json
import math


def remez_exp_degN(N=6, a=-6.0, b=6.0, iters=20, grid=4097):
    # Remez exchange method (scalar) for exp(x) on [a,b]
    xs = np.linspace(a, b, grid)
    f = np.exp(xs)
    # initial nodes: Chebyshev nodes
    t = np.cos((2*np.arange(N+2)+1)/(2*(N+2))*np.pi)
    xi = 0.5*(a+b)+0.5*(b-a)*t  # N+2 nodes
    for _ in range(iters):
        # Build system: sum c_k x^k + s* (-1)^i = f(x_i)
        V = np.vstack([xi**k for k in range(N+1)] +
                      [(-1.0)**np.arange(len(xi))]).T
        y = f = np.exp(xi)
        sol, *_ = np.linalg.lstsq(V, y, rcond=None)
        c = sol[:-1]
        s = sol[-1]
        # Compute error on dense grid
        p = sum(c[k]*xs**k for k in range(N+1))
        err = f - p
        # Find N+2 extrema of |err| with alternating signs
        idx = np.argpartition(-np.abs(err), N+2)[:N+2]
        idx.sort()
        xi = xs[idx]
        # Enforce alternation by sorting by x
        order = np.argsort(xi)
        xi = xi[order]
    return c.tolist(), float(np.max(np.abs(err)))


SAFE_NAME = re.compile(r"^[A-Za-z0-9._-]+$")  # allow only sane filenames
BASE_DIR = (Path(__file__).resolve().parent / "configs").resolve()


def safe_target(name: str) -> Path:
    if "/" in name or "\\" in name:
        raise ValueError("--out must be a filename, not a path")
    if not SAFE_NAME.fullmatch(name):
        raise ValueError("invalid filename; use letters, numbers, ., _, -")
    target = (BASE_DIR / name).resolve()
    # Ensure target stays under BASE_DIR (no traversal)
    try:
        target.relative_to(BASE_DIR)
    except ValueError:
        raise ValueError("refused path outside base directory")
    return target


def atomic_write_json(path: Path, payload: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    # Open securely; refuse following symlinks when supported
    flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    fd = os.open(path, flags, 0o600)
    with os.fdopen(fd, "w") as f:
        json.dump(payload, f, indent=2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--deg", type=int, default=6)
    ap.add_argument("--out", type=str, required=True,
                    help="output filename (saved under ./configs)")
    args = ap.parse_args()

    c, maxerr = remez_exp_degN(args.deg)
    S = 1 << 16
    cu = [int(round(ci * S)) for ci in c]

    out_path = safe_target(args.out)
    atomic_write_json(out_path, {
        "deg": args.deg,
        "coeff_float": c,
        "coeff_fixed": cu,
        "scale_bits": 16,
        "max_abs_err_float": maxerr,
    })
    print("wrote", str(out_path), "maxerr:", maxerr)


if __name__ == "__main__":
    main()
