from django.shortcuts import render

# Create your views here.
# apps/telemetry/views.py
from rest_framework.views import APIView
from django.utils.timezone import now

from apps.common.auth.cert_auth import DeviceCertificateAuthentication
from apps.common.utils.response import api_response

class HeartbeatView(APIView):
    # authentication_classes = [DeviceCertificateAuthentication]
    authentication_classes = []   # Bootstrap phase
    permission_classes = []

    def post(self, request):
        try:
            device = request.user
            device.last_seen = now()
            device.save(update_fields=["last_seen"])

            return api_response(True, "Heartbeat received")

        except Exception as e:
            return api_response(False, str(e), http_status=500)


class StatusView(APIView):
    authentication_classes = [DeviceCertificateAuthentication]

    def post(self, request):
        try:
            status_data = request.data

            # Save status (can be extended to DB / TSDB)
            return api_response(
                True,
                "Status updated",
                status_data
            )

        except Exception as e:
            return api_response(False, str(e), http_status=500)
