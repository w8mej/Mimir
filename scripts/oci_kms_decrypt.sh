
#!/usr/bin/env bash
set -euo pipefail
CIPH="$1"; OUT="$2"; KEY_OCID="${OCI_VAULT_KEY_OCID:?missing OCI_VAULT_KEY_OCID}"
PLAINTEXT_B64=$(oci kms crypto decrypt --key-id "$KEY_OCID" --ciphertext "$(cat "$CIPH")" --query 'data.plaintext' --raw-output)
echo "$PLAINTEXT_B64" | base64 -d > "$OUT"; chmod 600 "$OUT"; echo "[OCI KMS] Decrypted -> $OUT"
