
#!/usr/bin/env bash
set -euo pipefail
EIF="${1:-coordinator.eif}"
ENCLAVE_INFO=$(nitro-cli run-enclave --eif-path "$EIF" --cpu-count 2 --memory 4096 --enclave-cid 9 --debug-mode)
echo "$ENCLAVE_INFO"
CID=$(echo "$ENCLAVE_INFO" | sed -n 's/.*"EnclaveCID": \([0-9]*\).*//p')
echo "Enclave CID: $CID"
vsock-proxy 8080 $CID 8080 &
vsock-proxy 8081 $CID 8081 &
vsock-proxy 9090 $CID 9090 &
wait
