from rest_framework.views import APIView
from rest_framework import status
from django.utils.timezone import now

from .models import Certificate
from .services import sign_csr
from apps.common.utils.response import api_response

import tempfile
import uuid
import traceback


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

            if not csr_pem:
                return api_response(
                    False,
                    "CSR is required",
                    http_status=status.HTTP_400_BAD_REQUEST
                )

            # 🔹 Save CSR to temp file
            with tempfile.NamedTemporaryFile(delete=False, mode="w") as csr_file:
                csr_file.write(csr_pem)
                csr_path = csr_file.name

            # 🔹 Sign CSR (returns REAL cert path)
            cert_path = sign_csr(csr_path)

            # 🔹 Read signed certificate
            with open(cert_path, "r") as f:
                cert_pem = f.read()

            # 🔹 Persist certificate metadata (device mapping later)
            Certificate.objects.create(
                cert_type="DEVICE",
                serial_number=str(uuid.uuid4()),
                fingerprint="TO_BE_COMPUTED",
                expires_at=now().replace(year=now().year + 1)
            )

            return api_response(
                True,
                "Certificate issued successfully",
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
