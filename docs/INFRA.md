
# Infrastructure Guide (PoC)

## Docker
- `docker/Dockerfile.coordinator` reads `configs/security.yaml`. If `tls.enabled=true`, the coordinator serves gRPC over TLS/mTLS.
- Provide `certs/server.crt`, `certs/server.key`, and optional `certs/ca.crt` in the container (mounted at runtime).

## AWS Nitro Enclave
- Parent instance runs `enclave/parent_start_kms_proxy.sh` (vsock KMS proxy).
- Enclave ENTRYPOINT (`enclave/enclave_decrypt_and_start.sh`) decrypts `certs/server.key` via **KMS** (`kmstool_enclave_cli`) and enables TLS.
- Use `enclave/build_eif.sh` to build the EIF; `enclave/run_enclave.sh` to launch with `vsock-proxy` exposing ports.

## OCI Confidential VM
- Bring-your-own certs to `/opt/mimir/certs` and `configs/security.yaml` to enable mTLS; run `docker/compose.yml`.

## GitHub Actions
- `docker-images.yml` builds/pushes images and also produces an SBOM artifact.
- `enclave-eif.yml` builds an EIF (for Nitro) from the coordinator image and uploads it to S3.
