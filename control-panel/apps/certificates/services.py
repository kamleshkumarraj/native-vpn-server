import os
import platform
import subprocess
import uuid

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

if platform.system() == "Windows":
    CA_DIR = os.path.join(BASE_DIR, "ca")
    TMP_DIR = os.path.join(BASE_DIR, "tmp")
else:
    CA_DIR = "/etc/ipsec_ca"
    TMP_DIR = "/tmp"

CA_CERT = os.path.join(CA_DIR, "ca.crt")
CA_KEY = os.path.join(CA_DIR, "ca.key")


def ensure_dirs():
    os.makedirs(CA_DIR, exist_ok=True)
    os.makedirs(TMP_DIR, exist_ok=True)

    if not os.path.exists(CA_CERT):
        raise FileNotFoundError(f"CA certificate not found: {CA_CERT}")

    if not os.path.exists(CA_KEY):
        raise FileNotFoundError(f"CA private key not found: {CA_KEY}")


import os
import subprocess
import uuid
import tempfile

def sign_csr(csr_path, cert_type="device"):
    """
    cert_type:
      - "device"  → clientAuth
      - "gateway" → serverAuth
    """
    ensure_dirs()

    output_cert_path = os.path.join(
        TMP_DIR, f"{uuid.uuid4()}.crt"
    )

    # Decide EKU based on cert type
    if cert_type == "device":
        eku = "clientAuth"
    elif cert_type == "gateway":
        eku = "serverAuth"
    else:
        raise ValueError("cert_type must be 'device' or 'gateway'")

    # Create a temporary OpenSSL extension file
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        f.write(f"""
[ v3_req ]
basicConstraints = CA:FALSE
keyUsage = digitalSignature, keyEncipherment
extendedKeyUsage = {eku}
subjectKeyIdentifier = hash
authorityKeyIdentifier = keyid,issuer
""")
        ext_file = f.name

    try:
        subprocess.run(
            [
                "openssl", "x509", "-req",
                "-in", csr_path,
                "-CA", CA_CERT,
                "-CAkey", CA_KEY,
                "-CAcreateserial",
                "-out", output_cert_path,
                "-days", "365",
                "-sha256",
                "-extfile", ext_file,
                "-extensions", "v3_req"
            ],
            check=True
        )
    finally:
        os.remove(ext_file)

    return output_cert_path
