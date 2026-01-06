# agent/policy_sync.py
from api_client import mtls_get

def fetch_policies():
    from api_client import mtls_get


def fetch_policies():
    resp = mtls_get("/api/policies/")
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


def fetch_tunnels():
    return mtls_get("/api/tunnels/").json()["data"]
