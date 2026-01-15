import subprocess
from pathlib import Path
from typing import Tuple
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import pkcs12

# ---------------- CONFIG ----------------

CERT_DIR = Path("certs")
PFX_PASSWORD = b"KamleshVPN"

DEVICE_CERT = CERT_DIR / "device.crt"
DEVICE_KEY  = CERT_DIR / "device.key"
ROOT_CA     = CERT_DIR / "ca.crt"
PFX_FILE    = CERT_DIR / "device.pfx"


# ---------------- SYSTEM EXEC ----------------

def _run(cmd: list) -> Tuple[int, str, str]:
    p = subprocess.run(cmd, capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr


# ---------------- FILE CHECK ----------------

def _ensure_files():
    for f in [DEVICE_KEY, DEVICE_CERT, ROOT_CA]:
        if not f.exists():
            raise RuntimeError(f"Missing required file: {f}")


# ---------------- CERT LOADING ----------------

def _load_cert(path: Path):
    return x509.load_pem_x509_certificate(path.read_bytes(), default_backend())


def _load_key(path: Path):
    return serialization.load_pem_private_key(path.read_bytes(), password=None, backend=default_backend())


def _get_cn(cert: x509.Certificate) -> str:
    return cert.subject.get_attributes_for_oid(x509.NameOID.COMMON_NAME)[0].value


# ---------------- WINDOWS STORE ----------------

def _store_contains(store: str, cn: str) -> bool:
    rc, out, err = _run(["certutil", "-store", store])
    if rc != 0:
        raise RuntimeError(err)
    return cn in out


def device_cert_installed() -> bool:
    return _store_contains("My", _get_cn(_load_cert(DEVICE_CERT)))


def root_ca_installed() -> bool:
    return _store_contains("Root", _get_cn(_load_cert(ROOT_CA)))


# ---------------- PFX MANAGEMENT ----------------

def ensure_pfx_exists():
    """
    Create device.pfx only if missing.
    Uses Python crypto (no OpenSSL).
    """

    if PFX_FILE.exists():
        print("📦 device.pfx already exists")
        return

    print("📦 Creating device.pfx")

    _ensure_files()

    cert = _load_cert(DEVICE_CERT)
    key = _load_key(DEVICE_KEY)
    ca  = _load_cert(ROOT_CA)

    pfx = pkcs12.serialize_key_and_certificates(
        name=_get_cn(cert).encode(),
        key=key,
        cert=cert,
        cas=[ca],
        encryption_algorithm=serialization.BestAvailableEncryption(PFX_PASSWORD)
    )

    PFX_FILE.write_bytes(pfx)


# ---------------- INSTALL ----------------

def install_device_cert():
    rc, _, err = _run([
        "certutil",
        "-f",
        "-p", PFX_PASSWORD.decode(),
        "-importpfx",
        str(PFX_FILE)
    ])
    if rc != 0:
        raise RuntimeError(err)


def install_root_ca():
    rc, _, err = _run([
        "certutil",
        "-addstore",
        "-f",
        "Root",
        str(ROOT_CA)
    ])
    if rc != 0:
        raise RuntimeError(err)


# ---------------- VERIFY ----------------

def verify_installation():
    rc1, my, _ = _run(["certutil", "-store", "My"])
    rc2, root, _ = _run(["certutil", "-store", "Root"])
    if rc1 or rc2:
        raise RuntimeError("Certificate store read failed")
    return {"my": my, "root": root}


# ---------------- PUBLIC API ----------------

def window_install_vpn_certificates():
    print("🔐 Checking Windows PKI state")

    ensure_pfx_exists()

    if not device_cert_installed():
        print("📥 Installing device certificate")
        install_device_cert()
    else:
        print("✅ Device certificate already installed")

    if not root_ca_installed():
        print("🔒 Installing Root CA")
        install_root_ca()
    else:
        print("✅ Root CA already trusted")

    verify_installation()
    print("🎯 Windows ready for IKEv2 VPN")
