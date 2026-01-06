# agent/bootstrap.py
import platform
import requests
from config import CONTROL_PLANE_URL, AGENT_VERSION

def register_device():
    payload = {
        "hostname": platform.node(),
        "os_type": platform.system().upper(),
        "os_version": platform.version(),
        "agent_version": AGENT_VERSION,
    }

    resp = requests.post(
        f"{CONTROL_PLANE_URL}/api/devices/register/",
        json=payload,
        timeout=10
    )

    resp.raise_for_status()
    return resp.json()["data"]["device_id"]
