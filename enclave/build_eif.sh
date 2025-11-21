
#!/usr/bin/env bash
set -euo pipefail
IMG="${1:-ghcr.io/example/mpcprompt-coordinator:enclave}"
OUT="${2:-coordinator.eif}"
nitro-cli build-enclave --docker-uri "$IMG" --output-file "$OUT"
echo "EIF built: $OUT"
