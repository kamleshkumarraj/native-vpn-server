from ipsec.base import IPSecBase
import subprocess
import json


class WindowsIPSec(IPSecBase):
    """
    Windows IKEv2 VPN using Machine Certificate.
    One Tunnel = One VPN Profile
    Policies become VPN routes.
    """

    def _run_ps(self, script):
        return subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-NonInteractive",
                "-ExecutionPolicy", "Bypass",
                "-Command", script
            ],
            capture_output=True,
            text=True
        )

    def apply_tunnel(self, tunnel, policies):
        """
        tunnel  -> one VPN connection
        policies -> many routing rules (split/full tunnel)
        """

        vpn_name = f"NativeVPN-{tunnel['id']}"
        peer_ip = tunnel["gateway_ip"]

        # Check if any policy requires full tunnel
        full_tunnel = any(p["full_tunnel"] for p in policies)

        # Collect all subnets from split tunnel policies
        include_subnets = []
        exclude_subnets = []

        for p in policies:
            include_subnets.extend(p.get("include_subnets", []))
            exclude_subnets.extend(p.get("exclude_subnets", []))

        # Remove duplicates
        include_subnets = list(set(include_subnets))
        exclude_subnets = list(set(exclude_subnets))

        # If full tunnel, ignore include_subnets
        split_flag = "$False" if full_tunnel else "$True"

        # Build route commands
        route_cmds = ""

        if not full_tunnel:
            for subnet in include_subnets:
                route_cmds += f"""
Add-VpnConnectionRoute -ConnectionName "{vpn_name}" -DestinationPrefix "{subnet}" -PassThru
"""

        # Remove excluded routes if any
        for subnet in exclude_subnets:
            route_cmds += f"""
Remove-VpnConnectionRoute -ConnectionName "{vpn_name}" -DestinationPrefix "{subnet}" -ErrorAction SilentlyContinue
"""

        ps = f"""
$ErrorActionPreference = "SilentlyContinue"

# Remove old VPN if exists
Get-VpnConnection -Name "{vpn_name}" -ErrorAction SilentlyContinue | Remove-VpnConnection -Force

# Create IKEv2 VPN
Add-VpnConnection `
    -Name "{vpn_name}" `
    -ServerAddress "{peer_ip}" `
    -TunnelType IKEv2 `
    -AuthenticationMethod MachineCertificate `
    -EncryptionLevel Required `
    -SplitTunneling {split_flag} `
    -RememberCredential `
    -Force

# Set strong crypto
Set-VpnConnectionIPsecConfiguration `
    -ConnectionName "{vpn_name}" `
    -AuthenticationTransformConstants SHA256 `
    -CipherTransformConstants AES256 `
    -DHGroup Group14 `
    -EncryptionMethod AES256 `
    -IntegrityCheckMethod SHA256 `
    -PfsGroup None `
    -Force

# Apply policy routes
{route_cmds}

# Connect VPN
rasdial "{vpn_name}"
"""

        result = self._run_ps(ps)

        if result.returncode != 0:
            print(result.stderr)
            print(result.stdout)
            raise RuntimeError(f"Windows VPN setup failed:\n{result.stderr}\n{result.stdout}")

    def status(self):
        ps = """
Get-VpnConnection -AllUserConnection |
Select Name,ConnectionStatus,ServerAddress |
ConvertTo-Json
"""
        result = self._run_ps(ps)

        if result.returncode != 0:
            return {"status": "ERROR", "error": result.stderr}

        return {
            "status": "OK",
            "vpns": json.loads(result.stdout) if result.stdout else []
        }
