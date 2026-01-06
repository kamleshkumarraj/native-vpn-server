# agent/config.py
import platform
import os

CONTROL_PLANE_URL = "http://localhost:4000"
AGENT_VERSION = "1.0.0"


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

if platform.system() == "Linux":
    CERT_DIR = "/etc/ipsec-agent/certs"
else:
    # ✅ Windows / dev mode
    CERT_DIR = os.path.join(BASE_DIR, "certs")

KEY_PATH = os.path.join(CERT_DIR, "device.key")
CERT_PATH = os.path.join(CERT_DIR, "device.crt")
CA_CERT_PATH = os.path.join(CERT_DIR, "ca.crt")

