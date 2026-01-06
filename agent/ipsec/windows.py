# agent/ipsec/windows.py
from ipsec.base import IPSecBase
import subprocess

class WindowsIPSec(IPSecBase):

    def apply_tunnel(self, tunnel, policy):
        ps_script = f"""
New-NetIPsecMainModeCryptoSet -Name "MMCrypto" `
  -Encryption AES256 `
  -Integrity SHA256 `
  -DHGroup Group14

New-NetIPsecQuickModeCryptoSet -Name "QMCrypto" `
  -Encryption AES256 `
  -Integrity SHA256 `
  -PfsGroup PFS2048

New-NetIPsecRule -DisplayName "{tunnel['id']}" `
  -RemoteAddress {tunnel['peer_ip']} `
  -InboundSecurity Require `
  -OutboundSecurity Require `
  -MainModeCryptoSet MMCrypto `
  -QuickModeCryptoSet QMCrypto
"""
        subprocess.run(["powershell", "-Command", ps_script], check=True)

    def status(self):
        return subprocess.check_output(
            ["powershell", "Get-NetIPsecRule"]
        ).decode()


# Enable IKEv2
# Set-ItemProperty `
#   -Path HKLM:\SYSTEM\CurrentControlSet\Services\RasMan\Parameters `
#   -Name NegotiateDH2048_AES256 `
#   -Value 1

# # Open firewall
# netsh advfirewall firewall add rule name="IPSec IKE" dir=in protocol=UDP localport=500 action=allow
# netsh advfirewall firewall add rule name="IPSec NAT-T" dir=in protocol=UDP localport=4500 action=allow
