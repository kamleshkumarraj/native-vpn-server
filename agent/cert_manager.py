# agent/cert_manager.py
import subprocess
from config import KEY_PATH, CERT_PATH, CA_CERT_PATH, CONTROL_PLANE_URL, CERT_DIR
import requests
import os

def ensure_cert_dir():
    """
    Ensure certificate directory exists before using OpenSSL
    """
    try:
        os.makedirs(CERT_DIR, exist_ok=True)
    except Exception as e:
        raise RuntimeError(f"Failed to create cert directory: {e}")


def generate_key_and_csr(device_id):
    # 🔴 THIS LINE IS CRITICAL
    ensure_cert_dir()

    # 🔹 Generate private key
    subprocess.run(
        ["openssl", "genrsa", "-out", KEY_PATH, "4096"],
        check=True
    )

    csr_path = os.path.join(CERT_DIR, "device.csr")

    # 🔹 Generate CSR
    subprocess.run(
        [
            "openssl", "req", "-new",
            "-key", KEY_PATH,
            "-out", csr_path,
            "-subj", f"/CN={device_id}"
        ],
        check=True
    )

    with open(csr_path, "r") as f:
        return f.read()

def request_certificate(csr):
    """
    Bootstrap call: NO mTLS, NO client cert
    """
    resp = requests.post(
        f"{CONTROL_PLANE_URL}/api/certificates/sign/",
        json={"csr": csr},
        timeout=10
    )

    resp.raise_for_status()

    cert_pem = resp.json()["data"]["certificate"]

    # Save issued certificate
    with open(CERT_PATH, "w") as f:
        f.write(cert_pem)
