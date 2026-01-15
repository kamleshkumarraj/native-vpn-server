# agent/main.py

import time
import platform
import hashlib
import json

from bootstrap import register_device
from cert_manager import generate_key_and_csr, request_certificate
from policy_sync import fetch_policies, fetch_tunnels
from telemetry import send_heartbeat, send_status
from ipsec.linux import LinuxIPSec
from ipsec.windows import WindowsIPSec
from window_certs import window_install_vpn_certificates
from linux_cert import linux_install_vpn_certificates
from utils.update_status import send_status

def hash_state(tunnel, policies):
    """
    Used to detect changes.
    """
    blob = json.dumps({
        "tunnel": tunnel,
        "policies": policies
    }, sort_keys=True).encode()

    return hashlib.sha256(blob).hexdigest()


def main():
    device_id = register_device()

    csr = generate_key_and_csr(device_id)
    request_certificate(csr, device_id)

    
    install_vpn_certificates = linux_install_vpn_certificates if platform.system() == "Linux" else window_install_vpn_certificates
    
    install_vpn_certificates()

    ipsec = LinuxIPSec() if platform.system() == "Linux" else WindowsIPSec()

    last_state = None
    vpn_active = False

    while True:
        try:
            tunnel = fetch_tunnels(device_id)
            policies = fetch_policies(device_id)

            if not tunnel:
                if vpn_active:
                    ipsec.disconnect()
                    vpn_active = False

            elif not policies:
                if vpn_active:
                    ipsec.disconnect()
                    vpn_active = False

            else:
                current_state = hash_state(tunnel, policies)

                if current_state != last_state:
                    print("🔁 Applying VPN configuration")
                    ipsec.apply_tunnel(tunnel, policies)
                    send_status()
                    vpn_active = True
                    last_state = current_state

            send_heartbeat()
            send_status(ipsec.status())

        except Exception as e:
            print("Agent error:", e)

        time.sleep(30)


if __name__ == "__main__":
    main()
