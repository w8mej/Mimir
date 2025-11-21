
#!/usr/bin/env bash
set -euo pipefail
KEY_ARN="${KMS_KEY_ARN:?Set KMS_KEY_ARN}"; REGION="${AWS_REGION:-us-east-1}"
IN_PATH="${1:?ciphertext path required}"; OUT_PATH="${2:?plaintext output path required}"; ENC_CONTEXT_JSON="${3:-}"
B64=$(cat "$IN_PATH")
if [[ -n "$ENC_CONTEXT_JSON" ]]; then ENC_KV=$(echo "$ENC_CONTEXT_JSON" | jq -r 'to_entries|map("\(.key)=\(.value)")|join(",")'); PLAINTEXT=$(aws kms decrypt --key-id "$KEY_ARN" --region "$REGION" --encryption-context "$ENC_KV" --ciphertext-blob "$(echo "$B64" | base64 -d | base64)" --query 'Plaintext' --output text | base64 -d); else PLAINTEXT=$(aws kms decrypt --key-id "$KEY_ARN" --region "$REGION" --ciphertext-blob "$(echo "$B64" | base64 -d | base64)" --query 'Plaintext' --output text | base64 -d); fi
mkdir -p "$(dirname "$OUT_PATH")"; printf "%s" "$PLAINTEXT" > "$OUT_PATH"; chmod 600 "$OUT_PATH"; echo "[KMS] Decrypted -> $OUT_PATH"
