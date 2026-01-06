# agent/main.py
import time
import platform

from bootstrap import register_device
from cert_manager import generate_key_and_csr, request_certificate
from policy_sync import fetch_policies, fetch_tunnels
from telemetry import send_heartbeat, send_status
from ipsec.linux import LinuxIPSec
from ipsec.windows import WindowsIPSec

def main():
    device_id = register_device()
    csr = generate_key_and_csr(device_id)
    request_certificate(csr)

    ipsec = LinuxIPSec() if platform.system() == "Linux" else WindowsIPSec()

    while True:
        policies = fetch_policies()
        tunnels = fetch_tunnels()

        for t in tunnels:
            policy = next(p for p in policies if p["id"] == t["policy_id"])
            ipsec.apply_tunnel(t, policy)

        send_heartbeat()
        send_status(ipsec.status())

        time.sleep(30)

if __name__ == "__main__":
    main()
