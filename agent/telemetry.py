# agent/telemetry.py
from api_client import mtls_post

def send_heartbeat():
    mtls_post("/api/telemetry/heartbeat/", {})

def send_status(status):
    mtls_post("/api/telemetry/status/", {"status": status})
