
import cffi, os, pathlib, time, numpy as np, tempfile
ffi = cffi.FFI()
ffi.cdef("""void ct_add_u64(const unsigned long long* a, const unsigned long long* b, unsigned long long* out, int n);
void ct_sub_u64(const unsigned long long* a, const unsigned long long* b, unsigned long long* out, int n);
void ct_mulfx_u64(const long long* a, const long long* b, unsigned long long* out, int n, int scale_bits);
void ct_matmul_fx(const long long* A, const long long* B, unsigned long long* C, int M, int K, int N, int scale_bits);
""")
C_SRC = r"""#include <stdint.h>
void ct_add_u64(const unsigned long long* a, const unsigned long long* b, unsigned long long* out, int n){
  for(int i=0;i<n;i++){ out[i] = a[i] + b[i]; }
}
void ct_sub_u64(const unsigned long long* a, const unsigned long long* b, unsigned long long* out, int n){
  for(int i=0;i<n;i++){ out[i] = a[i] - b[i]; }
}
void ct_mulfx_u64(const long long* a, const long long* b, unsigned long long* out, int n, int scale_bits){
  for(int i=0;i<n;i++){
    __int128 prod = (__int128)a[i]*(__int128)b[i];
    long long r = (long long)(prod >> scale_bits);
    out[i] = (unsigned long long)r;
  }
}
void ct_matmul_fx(const long long* A, const long long* B, unsigned long long* C, int M, int K, int N, int scale_bits){
  for(int i=0;i<M;i++){
    for(int j=0;j<N;j++){
      __int128 acc = 0;
      for(int k=0;k<K;k++){
        __int128 prod = (__int128)A[i*K+k]*(__int128)B[k*N+j];
        acc += (prod >> scale_bits);
      }
      C[i*N+j] = (unsigned long long)((long long)acc);
    }
  }
}
"""
_mod = ffi.verify(C_SRC, extra_compile_args=['-O3'])
def mul_fx(a_i64: np.ndarray, b_i64: np.ndarray, scale_bits: int) -> np.ndarray:
    n = a_i64.size
    out = np.empty_like(a_i64, dtype=np.uint64)
    _mod.ct_mulfx_u64(ffi.cast("long long*", a_i64.ctypes.data), ffi.cast("long long*", b_i64.ctypes.data), ffi.cast("unsigned long long*", out.ctypes.data), n, scale_bits)
    return out
def matmul_fx(A_i64: np.ndarray, B_i64: np.ndarray, M, K, N, scale_bits: int) -> np.ndarray:
    C = np.empty((M,N), dtype=np.uint64)
    _mod.ct_matmul_fx(ffi.cast("long long*", A_i64.ctypes.data), ffi.cast("long long*", B_i64.ctypes.data), ffi.cast("unsigned long long*", C.ctypes.data), M,K,N, scale_bits)
    return C
