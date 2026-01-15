# # agent/cert_manager.py
# import subprocess
# from config import KEY_PATH, CERT_PATH, CA_CERT_PATH, CONTROL_PLANE_URL, CERT_DIR
# import requests
# import os

# def ensure_cert_dir():
#     """
#     Ensure certificate directory exists before using OpenSSL
#     """
#     try:
#         os.makedirs(CERT_DIR, exist_ok=True)
#     except Exception as e:
#         raise RuntimeError(f"Failed to create cert directory: {e}")


# def generate_key_and_csr(device_id):
#     # 🔴 THIS LINE IS CRITICAL
#     ensure_cert_dir()

#     # 🔹 Generate private key
#     subprocess.run(
#         ["openssl", "genrsa", "-out", KEY_PATH, "4096"],
#         check=True
#     )

#     csr_path = os.path.join(CERT_DIR, "device.csr")

#     # 🔹 Generate CSR
#     subprocess.run(
#         [
#             "openssl", "req", "-new",
#             "-key", KEY_PATH,
#             "-out", csr_path,
#             "-subj", f"/CN={device_id}"
#         ],
#         check=True
#     )

#     with open(csr_path, "r") as f:
#         return f.read()

# def request_certificate(csr):
#     """
#     Bootstrap call: NO mTLS, NO client cert
#     """
#     resp = requests.post(
#         f"{CONTROL_PLANE_URL}/api/certificates/sign/",
#         json={"csr": csr},
#         timeout=10
#     )

#     resp.raise_for_status()

#     cert_pem = resp.json()["data"]["certificate"]

#     # Save issued certificate
#     with open(CERT_PATH, "w") as f:
#         f.write(cert_pem)


# agent/cert_manager.py
# agent/cert_manager.py

from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa

import requests
import os

from config import (
    KEY_PATH,
    CERT_PATH,
    CERT_DIR,
    CONTROL_PLANE_URL
)


def ensure_cert_dir():
    """
    Ensure certificate directory exists
    """
    os.makedirs(CERT_DIR, exist_ok=True)


def generate_key_and_csr(device_id: str) -> str:
    """
    Generate RSA private key + CSR using cryptography.
    Returns CSR PEM string.
    """
    ensure_cert_dir()

    # 🔐 Generate private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=4096
    )

    # 💾 Save private key (PEM)
    with open(KEY_PATH, "wb") as key_file:
        key_file.write(
            private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            )
        )

    # 📄 Build CSR
    csr = (
        x509.CertificateSigningRequestBuilder()
        .subject_name(
            x509.Name([
                x509.NameAttribute(NameOID.COMMON_NAME, device_id)
            ])
        )
        .sign(private_key, hashes.SHA256())
    )

    csr_pem = csr.public_bytes(serialization.Encoding.PEM).decode()

    return csr_pem


def request_certificate(csr_pem: str, device_id: str) -> None:
    """
    Request signed certificate from control-plane.
    Bootstrap phase: no mTLS, no client cert.
    """

    resp = requests.post(
        f"{CONTROL_PLANE_URL}/api/certificates/sign/",
        json={"csr": csr_pem, "device_id": device_id},
        timeout=15
    )

    resp.raise_for_status()

    payload = resp.json()

    if not payload.get("success"):
        raise RuntimeError(
            f"Certificate issuance failed: {payload.get('message')}"
        )

    cert_pem = payload["data"]["certificate"]

    # 💾 Save issued certificate
    with open(CERT_PATH, "w") as cert_file:
        cert_file.write(cert_pem)
