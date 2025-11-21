
import numpy as np, time, statistics, pytest
from mpclib.ct.ctops import mul_fx, matmul_fx
@pytest.mark.sanity
def test_mul_fx_runs():
    a = np.random.randint(-(1<<30), 1<<30, size=4096, dtype=np.int64)
    b = np.random.randint(-(1<<30), 1<<30, size=4096, dtype=np.int64)
    out = mul_fx(a,b,16)
    assert out.shape == a.shape
@pytest.mark.sanity
def test_matmul_fx_runs_quick():
    A = np.random.randint(-(1<<30),1<<30,size=(32,32),dtype=np.int64)
    B = np.random.randint(-(1<<30),1<<30,size=(32,32),dtype=np.int64)
    C = matmul_fx(A,B,32,32,32,16)
    assert C.shape == (32,32)
@pytest.mark.sanity
def test_timing_uniformity_smoke():
    # very light check: distributions shouldn't split wildly across input classes
    samples = []
    for bias in [0,1]:
        times=[]
        for _ in range(20):
            A = np.random.randint(-(1<<30),1<<30,size=(32,32),dtype=np.int64)
            if bias: A = np.abs(A)
            B = np.random.randint(-(1<<30),1<<30,size=(32,32),dtype=np.int64)
            t0=time.perf_counter(); _=matmul_fx(A,B,32,32,32,16); dt=time.perf_counter()-t0
            times.append(dt)
        samples.append(times)
    # Welch's t-test heuristic
    m0, m1 = statistics.mean(samples[0]), statistics.mean(samples[1])
    assert abs(m0-m1) < max(m0,m1)*0.2  # crude bound
