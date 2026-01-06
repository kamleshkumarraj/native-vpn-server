# agent/config.py
CONTROL_PLANE_URL = "https://control-plane.company.local"
AGENT_VERSION = "1.0.0"

CERT_DIR = "/etc/ipsec-agent/certs"
KEY_PATH = f"{CERT_DIR}/device.key"
CERT_PATH = f"{CERT_DIR}/device.crt"
CA_CERT_PATH = f"{CERT_DIR}/ca.crt"
