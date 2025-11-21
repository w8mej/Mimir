
#!/usr/bin/env bash
set -euo pipefail
KEY_ARN="${KMS_KEY_ARN:?Set KMS_KEY_ARN}"; REGION="${AWS_REGION:-us-east-1}"
IN_PATH="${1:?input plaintext path required}"; OUT_PATH="${2:?output ciphertext path required}"; ENC_CONTEXT_JSON="${3:-}"
args=( --region "$REGION" --key-id "$KEY_ARN" --plaintext "fileb://$IN_PATH" )
if [[ -n "$ENC_CONTEXT_JSON" ]]; then args+=( --encryption-context "$(echo "$ENC_CONTEXT_JSON" | jq -r 'to_entries|map("\(.key)=\(.value)")|join(",")')" ); fi
blob=$(aws kms encrypt "${args[@]}" --query 'CiphertextBlob' --output text)
mkdir -p "$(dirname "$OUT_PATH")"; printf "%s" "$blob" > "$OUT_PATH"; chmod 600 "$OUT_PATH"
echo "[KMS] Wrote ciphertext to $OUT_PATH"
