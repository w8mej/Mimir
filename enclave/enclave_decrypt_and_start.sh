
#!/usr/bin/env bash
set -euo pipefail
CIPHERTEXT_PATH="${CIPHERTEXT_PATH:-/app/certs/server.key.enc}"
PLAINTEXT_PATH="${PLAINTEXT_PATH:-/app/certs/server.key}"
KEY_ARN="${KMS_KEY_ARN:-}"; AWS_REGION="${AWS_REGION:-us-east-1}"
ENC_CTX_JSON="${ENCRYPTION_CONTEXT_JSON:-}"
mkdir -p /app/certs
if [ -z "$KEY_ARN" ]; then echo "[Enclave] KMS_KEY_ARN not set"; exit 1; fi
if [ ! -f "$CIPHERTEXT_PATH" ]; then echo "[Enclave] Missing $CIPHERTEXT_PATH"; exit 1; fi
echo "[Enclave] Decrypting via KMS (vsock proxy)..."
ARGS=( decrypt --aws-region "$AWS_REGION" --ciphertext "fileb://$CIPHERTEXT_PATH" --key-id "$KEY_ARN" --output "fileb://$PLAINTEXT_PATH" )
if [[ -n "$ENC_CTX_JSON" ]]; then ENC_CTX_KV=$(echo "$ENC_CTX_JSON" | jq -r 'to_entries|map("\(.key)=\(.value)")|join(",")'); ARGS+=( --encryption-context "$ENC_CTX_KV" ); fi
kmstool_enclave_cli "${ARGS[@]}"
chmod 600 "$PLAINTEXT_PATH"; echo "[Enclave] TLS key decrypted at $PLAINTEXT_PATH"

# Write TLS settings to config if present
CFG="${MIMIR_SECURITY_CFG:-configs/security.yaml}"
if [ -f "$CFG" ]; then
  # enable TLS and point to decrypted key
  python - <<'PY'
import yaml,sys
p="configs/security.yaml"
with open(p,'r') as f: y=yaml.safe_load(f) or {}
y.setdefault('tls',{})
y['tls']['enabled']=True
y['tls']['server_key']='certs/server.key'
y['tls']['server_cert']=y['tls'].get('server_cert','certs/server.crt')
y['tls']['client_ca']=y['tls'].get('client_ca')  # optional
with open(p,'w') as f: yaml.safe_dump(y,f)
print("[Enclave] TLS enabled via",p)
PY
fi
exec python /app/coordinator/grpc_server.py

