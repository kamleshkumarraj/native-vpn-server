from django.shortcuts import render

# Create your views here.
# apps/certificates/views.py
from rest_framework.views import APIView
from rest_framework import status
from django.utils.timezone import now

from .models import Certificate
from .services import sign_csr
from apps.devices.models import Device
from apps.common.auth.cert_auth import DeviceCertificateAuthentication
from apps.common.utils.response import api_response

import tempfile
import uuid

class CertificateSignView(APIView):
    authentication_classes = [DeviceCertificateAuthentication]

    def post(self, request):
        try:
            device = request.user
            csr_pem = request.data.get("csr")

            if not csr_pem:
                return api_response(False, "CSR is required", http_status=400)

            with tempfile.NamedTemporaryFile(delete=False) as csr_file:
                csr_file.write(csr_pem.encode())
                csr_path = csr_file.name

            cert_path = f"/tmp/{uuid.uuid4()}.crt"
            sign_csr(csr_path, cert_path)

            cert_pem = open(cert_path).read()

            Certificate.objects.create(
                device=device,
                cert_type="DEVICE",
                serial_number=str(uuid.uuid4()),
                fingerprint="TO_BE_COMPUTED",
                expires_at=now().replace(year=now().year + 1)
            )

            return api_response(
                True,
                "Certificate issued successfully",
                {"certificate": cert_pem}
            )

        except Exception as e:
            return api_response(
                False,
                f"Certificate signing failed: {str(e)}",
                http_status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
