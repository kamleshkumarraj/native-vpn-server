import subprocess
from pathlib import Path
from typing import Tuple

# ---------------- CONFIG ----------------

CERT_DIR = Path("agent/certs")

DEVICE_CERT = CERT_DIR / "device.crt"
DEVICE_KEY  = CERT_DIR / "device.key"
ROOT_CA     = CERT_DIR / "ca.crt"

STRONGSWAN_CERTS   = Path("/etc/ipsec.d/certs")
STRONGSWAN_KEYS    = Path("/etc/ipsec.d/private")
STRONGSWAN_CACERTS = Path("/etc/ipsec.d/cacerts")


# ---------------- CORE EXEC ----------------

def _run(cmd: list) -> Tuple[int, str, str]:
    p = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    return p.returncode, p.stdout.strip(), p.stderr.strip()


# ---------------- FILE CHECK ----------------

def _ensure_files():
    for f in [DEVICE_CERT, DEVICE_KEY, ROOT_CA]:
        if not f.exists():
            raise RuntimeError(f"Missing required file: {f}")


# ---------------- CERT PARSING ----------------

def _get_cert_cn(cert_path: Path) -> str:
    rc, out, err = _run([
        "openssl", "x509",
        "-in", str(cert_path),
        "-noout",
        "-subject"
    ])
    if rc != 0:
        raise RuntimeError(err)

    return out.split("CN=")[1].strip()


# ---------------- STRONGSWAN STORE CHECK ----------------

def _strongswan_has_cert(cert_dir: Path, cn: str) -> bool:
    for cert in cert_dir.glob("*.crt"):
        rc, out, _ = _run([
            "openssl", "x509",
            "-in", str(cert),
            "-noout",
            "-subject"
        ])
        if rc == 0 and cn in out:
            return True
    return False


def device_cert_installed() -> bool:
    return _strongswan_has_cert(STRONGSWAN_CERTS, _get_cert_cn(DEVICE_CERT))


def root_ca_installed() -> bool:
    return _strongswan_has_cert(STRONGSWAN_CACERTS, _get_cert_cn(ROOT_CA))


# ---------------- INSTALL ----------------

def install_device_cert():
    STRONGSWAN_CERTS.mkdir(parents=True, exist_ok=True)
    STRONGSWAN_KEYS.mkdir(parents=True, exist_ok=True)

    _run(["cp", str(DEVICE_CERT), str(STRONGSWAN_CERTS)])
    _run(["cp", str(DEVICE_KEY),  str(STRONGSWAN_KEYS)])
    _run(["chmod", "600", str(STRONGSWAN_KEYS / DEVICE_KEY.name)])


def install_root_ca():
    STRONGSWAN_CACERTS.mkdir(parents=True, exist_ok=True)
    _run(["cp", str(ROOT_CA), str(STRONGSWAN_CACERTS)])


# ---------------- VERIFY ----------------

def verify_installation():
    rc1, certs, _ = _run(["ls", "-l", str(STRONGSWAN_CERTS)])
    rc2, keys, _  = _run(["ls", "-l", str(STRONGSWAN_KEYS)])
    rc3, cas, _   = _run(["ls", "-l", str(STRONGSWAN_CACERTS)])

    if rc1 or rc2 or rc3:
        raise RuntimeError("StrongSwan certificate folders not accessible")

    return {
        "certs": certs,
        "keys": keys,
        "cas": cas
    }


# ---------------- PUBLIC ENTRYPOINT ----------------

def linux_install_vpn_certificates():
    """
    Production-grade Linux PKI enrollment for Unified IPsec Agent
    """

    print("🔐 Verifying StrongSwan PKI state...")

    if not device_cert_installed():
        print("📥 Installing device certificate and key")
        install_device_cert()
    else:
        print("✅ Device certificate already installed")

    if not root_ca_installed():
        print("🔒 Installing Root CA")
        install_root_ca()
    else:
        print("✅ Root CA already trusted")

    print("✅ Verifying StrongSwan cert directories...")
    verify_installation()

    print("🎯 Linux device successfully enrolled into VPN PKI")
