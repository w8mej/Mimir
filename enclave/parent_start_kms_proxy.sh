
#!/usr/bin/env bash
set -euo pipefail
PORT=8000
BIN=$(command -v aws-nitro-enclaves-cli-proxy || echo "/usr/bin/aws-nitro-enclaves-cli-proxy")
if [ ! -x "$BIN" ]; then
  echo "Error: aws-nitro-enclaves-cli-proxy not found."; exit 1
fi
echo "[KMS Proxy] Starting on port ${PORT}..."
sudo "$BIN" --proxy-port "$PORT" &
PID=$!; trap 'kill $PID' SIGINT SIGTERM; wait $PID
