import hashlib
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from apps.devices.models import Device


def extract_cert_fingerprint(pem_cert: str) -> str:
    """
    Extract SHA256 fingerprint from X.509 certificate (DER bytes).
    """
    cert = x509.load_pem_x509_certificate(
        pem_cert.encode(),
        default_backend()
    )

    fingerprint = cert.fingerprint(hashes.SHA256()).hex()
    return fingerprint


class DeviceCertificateAuthentication(BaseAuthentication):
    """
    Zero-Trust Device Authentication using mTLS certificates.
    """

    def authenticate(self, request):
        # nginx / apache injects PEM here
        pem_cert = request.META.get("SSL_CLIENT_CERT")

        if not pem_cert:
            raise AuthenticationFailed("Client certificate not provided")

        fingerprint = extract_cert_fingerprint(pem_cert)

        device = Device.objects.filter(
            certificate_fingerprint=fingerprint,
            is_active=True
        ).first()

        if not device:
            raise AuthenticationFailed("Invalid, expired, or revoked device certificate")

        return (device, None)
