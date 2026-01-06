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


def sign_csr(csr_path):
    ensure_dirs()

    # ✅ ONLY THIS path must be used
    output_cert_path = os.path.join(
        TMP_DIR, f"{uuid.uuid4()}.crt"
    )

    subprocess.run(
        [
            "openssl", "x509", "-req",
            "-in", csr_path,
            "-CA", CA_CERT,
            "-CAkey", CA_KEY,
            "-CAcreateserial",
            "-out", output_cert_path,
            "-days", "365",
            "-sha256"
        ],
        check=True
    )

    # ✅ RETURN EXACT PATH THAT EXISTS
    return output_cert_path
