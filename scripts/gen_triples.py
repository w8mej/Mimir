
#!/usr/bin/env python3
import argparse
import os
import numpy as np
from mpclib.triples import gen_beaver_triple, save_triples_npz

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=".artifacts/triples.npz")
    ap.add_argument("--count", type=int, default=3)
    ap.add_argument("--m", type=int, default=4)
    ap.add_argument("--k", type=int, default=4)
    ap.add_argument("--n", type=int, default=4)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    rng = np.random.default_rng(args.seed)
    triples = []
    for _ in range(args.count):
        A, B, C = gen_beaver_triple((args.m, args.k), (args.k, args.n), rng)
        triples.append((A, B, C))

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    save_triples_npz(args.out, triples)
    print(f"Saved {args.count} triples to {args.out} for shapes ({args.m},{args.k})x({args.k},{args.n})")

if __name__ == "__main__":
    main()
