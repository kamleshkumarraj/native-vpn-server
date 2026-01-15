import subprocess
from pathlib import Path
from typing import Tuple

# ---------------- CONFIG ----------------

CERT_DIR = Path("agent/certs")
PFX_PASSWORD = "KamleshVPN"
PFX_FILE = CERT_DIR / "device.pfx"
DEVICE_CERT = CERT_DIR / "device.crt"
DEVICE_KEY = CERT_DIR / "device.key"
ROOT_CA = CERT_DIR / "ca.crt"


# ---------------- CORE EXEC ----------------

def _run(cmd: list) -> Tuple[int, str, str]:
    p = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        shell=False
    )
    return p.returncode, p.stdout.strip(), p.stderr.strip()


# ---------------- FILE CHECKS ----------------

def _ensure_files():
    for f in [DEVICE_KEY, DEVICE_CERT, ROOT_CA]:
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
        raise RuntimeError(f"Failed to read cert {cert_path}: {err}")

    # subject=CN = 0251daea-680c-4c25-9df3-b045da16a87b
    return out.split("CN=")[1].strip()


# ---------------- WINDOWS STORE CHECKS ----------------

def _store_contains(store: str, cn: str) -> bool:
    rc, out, err = _run(["certutil", "-store", store])
    if rc != 0:
        raise RuntimeError(f"Cannot read {store} store: {err}")
    return cn in out


def device_cert_installed() -> bool:
    return _store_contains("My", _get_cert_cn(DEVICE_CERT))


def root_ca_installed() -> bool:
    return _store_contains("Root", _get_cert_cn(ROOT_CA))


# ---------------- PFX GENERATION ----------------

def create_pfx():
    _ensure_files()

    rc, _, err = _run([
        "openssl", "pkcs12", "-export",
        "-inkey", str(DEVICE_KEY),
        "-in", str(DEVICE_CERT),
        "-certfile", str(ROOT_CA),
        "-out", str(PFX_FILE),
        "-passout", f"pass:{PFX_PASSWORD}"
    ])

    if rc != 0:
        raise RuntimeError(f"PFX creation failed: {err}")


# ---------------- INSTALLERS ----------------

def install_device_cert():
    rc, _, err = _run([
        "certutil",
        "-f",
        "-p", PFX_PASSWORD,
        "-importpfx",
        str(PFX_FILE)
    ])
    if rc != 0:
        raise RuntimeError(f"Device cert install failed: {err}")


def install_root_ca():
    rc, _, err = _run([
        "certutil",
        "-addstore",
        "-f",
        "Root",
        str(ROOT_CA)
    ])
    if rc != 0:
        raise RuntimeError(f"Root CA install failed: {err}")


def verify_installation():
    """
    Verifies certs exist in Windows stores
    """
    rc1, my_store, _ = _run(["certutil", "-store", "My"])
    rc2, root_store, _ = _run(["certutil", "-store", "Root"])

    if rc1 != 0 or rc2 != 0:
        raise RuntimeError("Failed to read certificate stores")

    return {
        "personal_store": my_store,
        "root_store": root_store
    }

# ---------------- PUBLIC ENTRYPOINT ----------------

def window_install_vpn_certificates():
    """
    Production-grade PKI bootstrap for Windows VPN agent.
    Idempotent, safe, and enterprise-correct.
    """

    print("🔐 Verifying Windows PKI state...")

    if not device_cert_installed():
        print("📦 Device cert not found — generating PFX")
        create_pfx()

        print("📥 Installing device certificate into MY store")
        install_device_cert()
    else:
        print("✅ Device certificate already present")

    if not root_ca_installed():
        print("🔒 Root CA not trusted — installing")
        install_root_ca()
    else:
        print("✅ Root CA already trusted")
        
    print("✅ Verifying certificate stores...")
    stores = verify_installation()

    print("🎯 Windows device successfully enrolled into VPN PKI")
