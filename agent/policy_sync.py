# agent/policy_sync.py
from api_client import mtls_get

def fetch_policies():
    return mtls_get("/api/policies/").json()["data"]

def fetch_tunnels():
    return mtls_get("/api/tunnels/").json()["data"]
