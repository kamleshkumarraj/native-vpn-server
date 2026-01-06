# apps/tunnels/services.py
def generate_strongswan_config(tunnel):
    return f"""
conn {tunnel.id}
    keyexchange=ikev2
    ike={tunnel.policy.encryption_algo}-{tunnel.policy.integrity_algo}-{tunnel.policy.dh_group}
    esp={tunnel.policy.encryption_algo}-{tunnel.policy.integrity_algo}
    left=%defaultroute
    leftcert=device-cert.pem
    right={tunnel.peer_ip}
    rightsubnet={tunnel.remote_subnet}
    auto=start
"""
