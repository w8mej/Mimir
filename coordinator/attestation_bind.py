
from dataclasses import dataclass
from typing import Optional
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import Encoding, PrivateFormat, NoEncryption
import datetime

@dataclass
class AttestationEvidence:
    kind: str              # 'sev-snp' or 'intel-tdx'
    report: bytes          # attestation report/quote
    nonce: Optional[bytes] = None
    measurement: Optional[bytes] = None

def verify_snp(report: bytes) -> bool:
    # TODO: integrate with AMD SNP attestation verification lib/service.
    return bool(report)

def verify_tdx(quote: bytes) -> bool:
    # TODO: integrate with Intel TDX attestation verification lib/service.
    return bool(quote)

def verify_and_issue_cert(e: AttestationEvidence, ca_key_pem: bytes, ca_cert_pem: bytes, common_name: str = "mpcparty") -> tuple[bytes, bytes]:
    ok = verify_snp(e.report) if e.kind == "sev-snp" else verify_tdx(e.report) if e.kind == "intel-tdx" else False
    if not ok:
        raise ValueError("Attestation verification failed")

    # Issue short-lived client certificate bound to measurement hash (as SAN/extension note)
    ca_key = serialization.load_pem_private_key(ca_key_pem, password=None)
    ca_cert = x509.load_pem_x509_certificate(ca_cert_pem)

    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    subject = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, common_name)])
    builder = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(ca_cert.subject)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.datetime.utcnow())
        .not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(hours=4))
        .add_extension(x509.SubjectAlternativeName([x509.DNSName("attested")]), critical=False)
        .add_extension(x509.UnrecognizedExtension(x509.ObjectIdentifier("1.3.6.1.4.1.57264.1.1"), e.measurement or b""), critical=False)
    )
    cert = builder.sign(private_key=ca_key, algorithm=hashes.SHA256())
    cert_pem = cert.public_bytes(Encoding.PEM)
    key_pem = key.private_bytes(Encoding.PEM, PrivateFormat.PKCS8, NoEncryption())
    return cert_pem, key_pem
