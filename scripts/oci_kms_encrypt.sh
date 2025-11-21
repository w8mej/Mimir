
#!/usr/bin/env bash
set -euo pipefail
KEY_OCID="${OCI_VAULT_KEY_OCID:?missing OCI_VAULT_KEY_OCID}"; IN_PATH="${1:?plaintext input required}"; OUT_PATH="${2:?ciphertext output required}"
B64=$(base64 -w0 "$IN_PATH"); RESP=$(oci kms crypto encrypt --key-id "$KEY_OCID" --plaintext "$B64" --query 'data.ciphertext' --raw-output)
mkdir -p "$(dirname "$OUT_PATH")"; printf "%s" "$RESP" > "$OUT_PATH"; chmod 600 "$OUT_PATH"; echo "[OCI KMS] Wrote ciphertext -> $OUT_PATH"
