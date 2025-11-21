
# AWS Nitro Enclaves Deployment (Prototype)

This directory contains helper scripts to package the **coordinator** into a Nitro Enclave EIF
and run it inside an enclave. Communication uses a vsock proxy on the parent instance that forwards
TCP ports into the enclave.

> DISCLAIMER: This is a dev-friendly scaffold. For production, build a minimal rootfs, disable shell,
> and pass attestation material into the enclave; bind to TLS with enclave-held keys.

## Layout

- `enclave/Dockerfile.enclave` — enclave rootfs image (builder target only)
- `enclave/build_eif.sh` — builds the EIF from the Docker image using `nitro-cli`
- `enclave/run_enclave.sh` — launches the EIF and sets up vsock proxies
- `enclave/systemd/` — optional unit files

## Prereqs on parent EC2

- Instance type with **Nitro Enclaves** support (e.g., `c5.*`, `m5.*`, `r5.*`) and Enclaves enabled.
- Amazon Linux 2 or Ubuntu with `nitro-cli` installed.
- Docker installed.
- Security group allowing ports: `8080`, `8081`, `9090` (or adjust).

## Quickstart

```bash
# on parent host
sudo yum install -y aws-nitro-enclaves-cli docker
sudo usermod -aG ne docker $USER

cd /opt/mimir
docker build -f docker/Dockerfile.coordinator -t mimir/coordinator:enclave .

# Build EIF
sudo enclave/build_eif.sh mpcprompt/coordinator:enclave mpcprompt-coordinator.eif

# Run enclave
sudo enclave/run_enclave.sh mpcprompt-coordinator.eif
```
