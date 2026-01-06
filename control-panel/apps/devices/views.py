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

            hostname = payload["hostname"]
            os_type = payload["os_type"]
            os_version = payload["os_version"]
            agent_version = payload["agent_version"]
            ip_address = request.META.get("REMOTE_ADDR")

            # 🔹 Check if device already exists
            device = Device.objects.filter(
                hostname=hostname,
                os_type=os_type
            ).first()

            if device:
                # 🔹 Update last seen / IP / agent version
                device.ip_address = ip_address
                device.agent_version = agent_version
                device.last_seen = now()
                device.save(update_fields=[
                    "ip_address",
                    "agent_version",
                    "last_seen"
                ])

                return api_response(
                    True,
                    "Device already registered",
                    {"device_id": str(device.id)},
                    status.HTTP_200_OK
                )

            # 🔹 New device registration
            device = Device.objects.create(
                hostname=hostname,
                os_type=os_type,
                os_version=os_version,
                ip_address=ip_address,
                agent_version=agent_version,
                certificate_fingerprint="PENDING",
                last_seen=now()
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
