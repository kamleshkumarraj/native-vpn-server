# agent/ipsec/linux.py

from ipsec.base import IPSecBase
import subprocess
from pathlib import Path


class LinuxIPSec(IPSecBase):

    def apply_tunnel(self, tunnel, policies):
        """
        tunnel  -> ONE IKEv2 tunnel
        policies -> MANY traffic selectors (CHILD_SA)
        """

        conn_name = f"device-{tunnel['id']}"
        peer_ip = tunnel["gateway_ip"]

        # Determine crypto from highest priority policy
        policies = sorted(policies, key=lambda p: p["priority"])
        crypto = policies[0]

        ike = f"{crypto['encryption_algo']}-{crypto['integrity_algo']}-{crypto['dh_group']}"
        esp = f"{crypto['encryption_algo']}-{crypto['integrity_algo']}"

        # Check if any policy requires full tunnel
        full_tunnel = any(p["full_tunnel"] for p in policies)

        child_sas = ""

        if full_tunnel:
            child_sas += f"""
    net {{
        local_ts = 0.0.0.0/0
        remote_ts = 0.0.0.0/0
    }}
"""
        else:
            for p in policies:
                for subnet in p["include_subnets"]:
                    name = subnet.replace("/", "_").replace(".", "_")
                    child_sas += f"""
    {name} {{
        local_ts = 0.0.0.0/0
        remote_ts = {subnet}
    }}
"""

        config = f"""
connections {{
  {conn_name} {{
    version = 2
    remote_addrs = {peer_ip}

    local {{
      auth = pubkey
      certs = device.crt
    }}

    remote {{
      auth = pubkey
    }}

    proposals = {ike}
    children {{
        {child_sas}
    }}
  }}
}}
"""

        Path("/etc/swanctl/conf.d").mkdir(parents=True, exist_ok=True)
        Path(f"/etc/swanctl/conf.d/{conn_name}.conf").write_text(config)

        # Load & connect
        subprocess.run(["swanctl", "--load-all"], check=True)
        subprocess.run(["swanctl", "--initiate", "--ike", conn_name], check=True)

    def status(self):
        return subprocess.check_output(["swanctl", "--list-sas"]).decode()
