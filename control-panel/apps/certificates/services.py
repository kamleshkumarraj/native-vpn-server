# apps/certificates/services.py
import subprocess
from pathlib import Path

CA_CERT = "/etc/ipsec_ca/ca.crt"
CA_KEY = "/etc/ipsec_ca/ca.key"

def sign_csr(csr_path, output_cert):
    subprocess.run([
        "openssl", "x509", "-req",
        "-in", csr_path,
        "-CA", CA_CERT,
        "-CAkey", CA_KEY,
        "-CAcreateserial",
        "-out", output_cert,
        "-days", "365",
        "-sha256"
    ], check=True)
