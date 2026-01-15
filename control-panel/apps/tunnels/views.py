# apps/tunnels/views.py

from rest_framework.views import APIView
from rest_framework import status
from django.utils import timezone

from .models import Tunnel
from apps.common.utils.response import api_response
from apps.devices.models import Device
from apps.gateways.models import VPNGateway
from apps.common.auth.cert_auth import DeviceCertificateAuthentication

class TunnelView(APIView):
    # authentication_classes = [DeviceCertificateAuthentication]
    authentication_classes = []   # Bootstrap phase
    permission_classes = []
    def get(self, request):
        try:
            device_id = request.query_params.get("device_id")

            if not device_id:
                return api_response(False, "device_id is required", http_status=400)

            tunnel = Tunnel.objects.select_related("device", "gateway")\
                                .filter(device_id=device_id)\
                                .first()

            if not tunnel:
                return api_response(True, "No tunnel for this device", None)

            data = {
                "id": tunnel.id,
                "device": tunnel.device.hostname,
                "gateway": tunnel.gateway.name,
                "gateway_ip": tunnel.gateway.public_ip,
                "status": tunnel.status,
                "virtual_ip": tunnel.virtual_ip,
                "public_ip": tunnel.device_public_ip,
                "bytes_in": tunnel.bytes_in,
                "bytes_out": tunnel.bytes_out,
                "last_seen": tunnel.last_seen,
                "is_active": tunnel.is_active
            }

            return api_response(True, "Tunnel fetched", data)

        except Exception as e:
            return api_response(False, str(e), http_status=500)
    def post(self, request):
        """
        Create ONE tunnel per device.
        If tunnel already exists, do not create another.
        """
        try:
            device_id = request.data.get("device_id")
            gateway_id = request.data.get("gateway_id")

            device = Device.objects.filter(id=device_id).first()
            if not device:
                return api_response(False, "Invalid device_id", http_status=400)

            # One device → one tunnel
            if hasattr(device, "tunnel"):
                return api_response(False, "Tunnel already exists for this device", http_status=400)

            # If gateway not specified, pick any active gateway
            if gateway_id:
                gateway = VPNGateway.objects.filter(id=gateway_id, is_active=True).first()
            else:
                gateway = VPNGateway.objects.filter(is_active=True).first()

            if not gateway:
                return api_response(False, "No active VPN Gateway available", http_status=400)

            tunnel = Tunnel.objects.create(
                device=device,
                gateway=gateway,
                connection_name=f"vpn-{device.id}",
                status="DISCONNECTED",
                is_active=False
            )

            return api_response(
                True,
                "Tunnel created",
                {
                    "tunnel_id": tunnel.id,
                    "device": device.hostname,
                    "gateway": gateway.name
                },
                status.HTTP_201_CREATED
            )

        except Exception as e:
            return api_response(False, str(e), http_status=400)

from django.utils.timezone import now
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .models import Tunnel
from apps.common.utils.response import api_response


class TunnelStatusView(APIView):
    """
    Agent → Control Panel
    Updates runtime tunnel state after VPN is connected
    Uses mTLS (device certificate)
    """

    permission_classes = []
    authentication_classes = []

    def put(self, request):
        try:
            device = request.user   # Device from certificate auth

            tunnel = Tunnel.objects.filter(device=device).first()
            if not tunnel:
                return api_response(
                    False,
                    "Tunnel not assigned to this device",
                    http_status=status.HTTP_404_NOT_FOUND
                )

            data = request.data

            # Update runtime fields
            tunnel.status = "ESTABLISHED" if data.get("status") == "CONNECTED" else "FAILED"
            tunnel.virtual_ip = data.get("virtual_ip")
            tunnel.ike_sa_id = data.get("ike_sa_id")
            tunnel.device_public_ip = data.get("device_public_ip")
            tunnel.last_seen = now()

            if tunnel.status == "ESTABLISHED" and not tunnel.connected_at:
                tunnel.connected_at = now()

            tunnel.save()

            return api_response(
                True,
                "Tunnel status updated",
                {
                    "tunnel_id": tunnel.id,
                    "status": tunnel.status
                },
                status.HTTP_200_OK
            )

        except Exception as e:
            return api_response(
                False,
                f"Failed to update tunnel: {str(e)}",
                http_status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
