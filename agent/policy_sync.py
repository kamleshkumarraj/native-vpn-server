# agent/policy_sync.py
from api_client import mtls_get

def fetch_policies():
    from api_client import mtls_get


def fetch_policies(device_id):
    resp = mtls_get(f"/api/policies/?device_id={device_id}")
    payload = resp.json()
    print(payload)
    if not payload.get("success"):
        raise RuntimeError(
            f"Policy fetch failed: {payload.get('message')}"
        )

    if "data" not in payload:
        raise RuntimeError(
            f"Invalid policy response format: {payload}"
        )

    return payload["data"]


def fetch_tunnels(device_id):
    return mtls_get(f"/api/tunnels/?device_id={device_id}").json()["data"]
