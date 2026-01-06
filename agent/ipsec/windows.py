from ipsec.base import IPSecBase
import subprocess
import json


class WindowsIPSec(IPSecBase):
    """
    Windows native IPsec implementation.
    Uses Windows secure defaults for crypto.
    Requires Administrator privileges.
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

    def apply_tunnel(self, tunnel, policy):
        rule_name = tunnel["id"]
        peer_ip = tunnel["peer_ip"]

        ps_script = f"""
# Remove existing rule (idempotent)
Get-NetIPsecRule -DisplayName "{rule_name}" -ErrorAction SilentlyContinue | Remove-NetIPsecRule

# Create IPsec rule (Windows chooses crypto defaults)
New-NetIPsecRule `
  -DisplayName "{rule_name}" `
  -RemoteAddress {peer_ip} `
  -InboundSecurity Require `
  -OutboundSecurity Require `
  -Profile Any
"""

        result = self._run_ps(ps_script)

        if result.returncode != 0:
            raise RuntimeError(
                f"Windows IPsec apply failed:\\n{result.stderr}"
            )

    def status(self):
        try:
            result = self._run_ps(
                "Get-NetIPsecMainModeSA | "
                "Select LocalAddress,RemoteAddress,State | ConvertTo-Json"
            )

            if result.returncode != 0:
                return {"status": "ERROR", "error": result.stderr}

            return {
                "status": "OK",
                "sas": json.loads(result.stdout) if result.stdout else []
            }

        except Exception as e:
            return {"status": "ERROR", "error": str(e)}
