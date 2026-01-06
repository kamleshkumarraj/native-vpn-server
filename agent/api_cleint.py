# agent/api_client.py
import requests
from config import CONTROL_PLANE_URL, CERT_PATH, KEY_PATH, CA_CERT_PATH

def mtls_get(endpoint):
    return requests.get(
        f"{CONTROL_PLANE_URL}{endpoint}",
        cert=(CERT_PATH, KEY_PATH),
        verify=CA_CERT_PATH,
        timeout=10
    )

def mtls_post(endpoint, payload):
    return requests.post(
        f"{CONTROL_PLANE_URL}{endpoint}",
        json=payload,
        cert=(CERT_PATH, KEY_PATH),
        verify=CA_CERT_PATH,
        timeout=10
    )
