import hashlib
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from apps.devices.models import Device


def extract_cert_fingerprint(pem_cert: str) -> str:
    """
    PEM certificate se SHA256 fingerprint nikalta hai
    """
    # PEM header/footer hatao
    cert_body = pem_cert.replace(
        "-----BEGIN CERTIFICATE-----", ""
    ).replace(
        "-----END CERTIFICATE-----", ""
    ).replace("\n", "")

    cert_bytes = cert_body.encode()
    fingerprint = hashlib.sha256(cert_bytes).hexdigest()
    return fingerprint


class DeviceCertificateAuthentication(BaseAuthentication):
    """
    Certificate based authentication for Agent / Gateway
    """

    def authenticate(self, request):
        """
        Ye function har request par chalega
        """
        # 🔹 Web server (nginx / apache) client cert yahan inject karega
        pem_cert = request.META.get("SSL_CLIENT_CERT")

        if not pem_cert:
            raise AuthenticationFailed("Client certificate not provided")

        fingerprint = extract_cert_fingerprint(pem_cert)

        # 🔹 Device DB se match karo
        device = Device.objects.filter(
            certificate_fingerprint=fingerprint,
            is_active=True
        ).first()

        if not device:
            raise AuthenticationFailed("Invalid or revoked device certificate")

        # DRF expects (user, auth)
        return (device, None)
