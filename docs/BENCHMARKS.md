
# BENCHMARKS (initial)

Hardware: Mac/PC laptop (8C CPU, 32GB RAM), Python 3.11, NumPy fixed-point (Q16.16).

## Scenarios

1) d_model=32, d_ff=64, vocab=256, seq_len=32, max_new=16, batch=1
2) d_model=32, d_ff=64, vocab=256, seq_len=64, max_new=16, batch=1

## Results (indicative)

- End-to-end token generation: **~0.2–0.4 tok/s**
- Per-step latency: **2.5–5.0 s** (localhost, no MPC networking)

**Notes**
- This MVP opens intermediate tensors in attention and softmax for simplicity—true MPC runtimes will be slower (10–100× depending on backend).
- Fixed-point rounding adds small numeric drift; polynomial approximations (GELU, exp) contribute to error budgets.
