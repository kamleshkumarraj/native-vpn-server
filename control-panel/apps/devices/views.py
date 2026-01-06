from django.shortcuts import render

# Create your views here.
# apps/devices/views.py
from rest_framework.views import APIView
from rest_framework import status
from django.utils.timezone import now

from .models import Device
from apps.common.utils.response import api_response

class DeviceRegisterView(APIView):
    authentication_classes = []   # Bootstrap phase
    permission_classes = []

    def post(self, request):
        try:
            payload = request.data

            device = Device.objects.create(
                hostname=payload["hostname"],
                os_type=payload["os_type"],
                os_version=payload["os_version"],
                ip_address=request.META.get("REMOTE_ADDR"),
                agent_version=payload["agent_version"],
                certificate_fingerprint="PENDING"
            )

            return api_response(
                True,
                "Device registered successfully",
                {"device_id": str(device.id)},
                status.HTTP_201_CREATED
            )

        except KeyError as e:
            return api_response(
                False,
                f"Missing required field: {str(e)}",
                http_status=status.HTTP_400_BAD_REQUEST
            )

        except Exception as e:
            return api_response(
                False,
                f"Device registration failed: {str(e)}",
                http_status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
