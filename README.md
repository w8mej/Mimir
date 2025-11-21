
# Mimir (PoC)
This is a stricter PoC prototype with real protobufs/gRPC, stronger MPC (Beaver matmul + MACed opens), and fuller docs.


## Enclave boot (Nitro) – KMS → mTLS
The enclave ENTRYPOINT (`enclave/enclave_decrypt_and_start.sh`) decrypts the **server private key** via KMS (vsock) and enables TLS in `configs/security.yaml`. Parties should call `RegisterParty` with SEV‑SNP/TDX attestation; the coordinator verifies policy and issues a **short‑lived client cert** bound to the measurement OID to enforce **mTLS** on subsequent MPC RPCs.
