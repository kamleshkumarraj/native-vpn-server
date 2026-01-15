import subprocess
import requests
import re
import json

API_STATUS_URL = "http://localhost:4000/api/tunnel/status/"   # change to your CP URL


def get_public_ip():
    try:
        return subprocess.check_output(
            ["powershell", "-Command", "(Invoke-WebRequest -Uri https://ifconfig.me).Content"]
        ).decode().strip()
    except:
        return None


def get_vpn_virtual_ip(vpn_name):
    ps = f"""
(Get-NetIPAddress -InterfaceAlias "{vpn_name}" -AddressFamily IPv4).IPAddress
"""
    try:
        return subprocess.check_output(
            ["powershell", "-Command", ps]
        ).decode().strip()
    except:
        return None


def get_ike_sa_id(vpn_name):
    ps = "ipsec statusall"
    try:
        out = subprocess.check_output(ps, shell=True).decode()
        match = re.search(rf"{vpn_name}\[\d+\]", out)
        return match.group(0) if match else None
    except:
        return None


def send_status(vpn_name, device_cert_path):
    virtual_ip = get_vpn_virtual_ip(vpn_name)
    public_ip = get_public_ip()
    ike_sa = get_ike_sa_id(vpn_name)

    payload = {
        "status": "CONNECTED",
        "virtual_ip": virtual_ip,
        "ike_sa_id": ike_sa,
        "device_public_ip": public_ip
    }

    # Send using mTLS
    requests.post(
        API_STATUS_URL,
        json=payload,
        cert=(device_cert_path, "device.key"),
        verify="ca.crt"
    )
