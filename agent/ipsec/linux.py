# agent/ipsec/linux.py
from ipsec.base import IPSecBase
import subprocess

class LinuxIPSec(IPSecBase):

    def apply_tunnel(self, tunnel, policy):
        conn_name = tunnel["id"]

        config = f"""
conn {conn_name}
    keyexchange=ikev2
    ike={policy['encryption_algo']}-{policy['integrity_algo']}-{policy['dh_group']}
    esp={policy['encryption_algo']}-{policy['integrity_algo']}
    left=%defaultroute
    leftcert=device.crt
    right={tunnel['peer_ip']}
    rightsubnet={tunnel['remote_subnet']}
    auto=start
"""

        open(f"/etc/strongswan/ipsec.d/{conn_name}.conf", "w").write(config)

        subprocess.run(["systemctl", "restart", "strongswan"], check=True)

    def status(self):
        return subprocess.check_output(["ipsec", "statusall"]).decode()



# Install
# apt install strongswan -y

# # Ports
# ufw allow 500/udp
# ufw allow 4500/udp

# # Start
# systemctl enable strongswan
# systemctl start strongswan

# # Verify
# ipsec statusall
