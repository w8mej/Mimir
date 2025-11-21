
from dataclasses import dataclass
from typing import Optional

@dataclass
class AttestationEvidence:
    kind: str
    quote: bytes
    nonce: Optional[bytes] = None
    policy: Optional[dict] = None
    tls_client_subject: Optional[str] = None
    tls_client_akid: Optional[str] = None

def verify_sev_snp(e: AttestationEvidence) -> bool:
    return bool(e.quote) and e.kind == "sev-snp"

def verify_intel_tdx(e: AttestationEvidence) -> bool:
    return bool(e.quote) and e.kind == "intel-tdx"

def validate_attestation(e: AttestationEvidence) -> bool:
    if e.kind == "sev-snp":
        return verify_sev_snp(e)
    if e.kind == "intel-tdx":
        return verify_intel_tdx(e)
    return False
