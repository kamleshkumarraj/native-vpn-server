# agent/cert_manager.py
import subprocess
from config import KEY_PATH, CERT_PATH, CA_CERT_PATH, CONTROL_PLANE_URL
import requests

def generate_key_and_csr(device_id):
    subprocess.run([
        "openssl", "genrsa", "-out", KEY_PATH, "4096"
    ], check=True)

    csr_path = "/tmp/device.csr"
    subprocess.run([
        "openssl", "req", "-new",
        "-key", KEY_PATH,
        "-out", csr_path,
        "-subj", f"/CN={device_id}"
    ], check=True)

    csr = open(csr_path).read()
    return csr

def request_certificate(csr):
    resp = requests.post(
        f"{CONTROL_PLANE_URL}/api/certificates/sign/",
        json={"csr": csr},
        cert=(CERT_PATH, KEY_PATH),
        verify=CA_CERT_PATH
    )

    resp.raise_for_status()
    cert = resp.json()["data"]["certificate"]
    open(CERT_PATH, "w").write(cert)
