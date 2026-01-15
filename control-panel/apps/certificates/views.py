# apps/certificates/views.py

import tempfile
import uuid
import traceback
from django.utils.timezone import now
from django.db import transaction
from rest_framework.views import APIView
from rest_framework import status
from cryptography import x509
from cryptography.hazmat.primitives import hashes

from .models import Certificate
from .services import sign_csr
from apps.devices.models import Device
from apps.gateways.models import VPNGateway
from apps.tunnels.models import Tunnel
from apps.common.utils.response import api_response


class CertificateSignView(APIView):
    """
    Bootstrap certificate signing endpoint
    NO authentication / NO mTLS
    """
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        try:
            csr_pem = request.data.get("csr")
            device_id = request.data.get("device_id")

            if not csr_pem or not device_id:
                return api_response(False, "csr and device_id required", 400)

            device = Device.objects.filter(id=device_id).first()
            if not device:
                return api_response(False, "Invalid device", 400)

            with transaction.atomic():

                # ---------------------------
                # 1) Save CSR
                # ---------------------------
                with tempfile.NamedTemporaryFile(delete=False, mode="w") as csr_file:
                    csr_file.write(csr_pem)
                    csr_path = csr_file.name

                # ---------------------------
                # 2) Sign CSR (DO NOT CHANGE)
                # ---------------------------
                cert_path = sign_csr(csr_path)

                # ---------------------------
                # 3) Read cert
                # ---------------------------
                with open(cert_path, "r") as f:
                    cert_pem = f.read()

                cert = x509.load_pem_x509_certificate(cert_pem.encode())
                fingerprint = cert.fingerprint(hashes.SHA256()).hex()
                expires_at = cert.not_valid_after

                # ---------------------------
                # 4) Save Certificate
                # ---------------------------
                Certificate.objects.create(
                    device=device,
                    cert_type="DEVICE",
                    serial_number=str(cert.serial_number),
                    fingerprint=fingerprint,
                    expires_at=expires_at
                )

                # ---------------------------
                # 5) Activate Device
                # ---------------------------
                device.certificate_fingerprint = fingerprint
                device.is_active = True
                device.save()

                # ---------------------------
                # 6) Assign Gateway & Create Tunnel
                # ---------------------------
                gateway = VPNGateway.objects.filter(is_active=True).first()
                if not gateway:
                    raise Exception("No active VPN gateway available")

                Tunnel.objects.get_or_create(
                    device=device,
                    defaults={
                        "gateway": gateway,
                        "connection_name": f"vpn-{device.id}",
                        "status": "DISCONNECTED",
                        "is_active": True
                    }
                )

            # ---------------------------
            # 7) Return certificate
            # ---------------------------
            return api_response(
                True,
                "Certificate issued and device approved",
                {"certificate": cert_pem},
                status.HTTP_200_OK
            )

        except Exception as e:
            traceback.print_exc()
            return api_response(
                False,
                f"Certificate signing failed: {str(e)}",
                http_status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
