# apps/policies/views.py

from rest_framework.views import APIView
from rest_framework import status
from django.shortcuts import get_object_or_404

from .models import IPSecPolicy
from .serializers import IPSecPolicySerializer
from apps.common.utils.response import api_response
from apps.tunnels.models import Tunnel
from apps.common.auth.cert_auth import DeviceCertificateAuthentication
from apps.devices.models import Device

class PolicyView(APIView):
    """
    Policy API aligned with:
    Device → Tunnel → Policies → IPsec
    """
    # authentication_classes = [DeviceCertificateAuthentication] 
    authentication_classes = []   # Bootstrap phase
    permission_classes = []
    def get(self, request):
        
        try:
            # Device is identified via certificate
            device_id = request.query_params.get("device_id")
            device  = Device.objects.filter(id=device_id).first()

            # Get device tunnel
            tunnel = getattr(device, "tunnel", None)
            if not tunnel:
                return api_response(
                    True,
                    "No tunnel for this device",
                    []
                )

            # Fetch only policies attached to this tunnel
            policies = IPSecPolicy.objects.filter(
                tunnels=tunnel,
                is_active=True
            ).order_by("priority")

            serializer = IPSecPolicySerializer(policies, many=True)

            return api_response(
                True,
                "Policies fetched",
                serializer.data,
                status.HTTP_200_OK
            )

        except Exception as e:
            return api_response(
                False,
                f"Failed to fetch policies: {str(e)}",
                http_status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def post(self, request):
        """
        Admin creates a new policy.
        Does NOT attach to any tunnel yet.
        """
        try:
            serializer = IPSecPolicySerializer(data=request.data)
            if not serializer.is_valid():
                return api_response(False, serializer.errors, http_status=400)

            policy = serializer.save()

            return api_response(
                True,
                "Policy created",
                {"id": policy.id},
                status.HTTP_201_CREATED
            )

        except Exception as e:
            return api_response(False, str(e), http_status=400)

    def put(self, request, pk):
        """
        Update policy attributes.
        Does not control tunnel assignment.
        """
        try:
            policy = get_object_or_404(IPSecPolicy, pk=pk)

            serializer = IPSecPolicySerializer(
                policy, data=request.data, partial=True
            )

            if not serializer.is_valid():
                return api_response(False, serializer.errors, http_status=400)

            serializer.save()

            return api_response(True, "Policy updated")

        except Exception as e:
            return api_response(False, str(e), http_status=400)

    def delete(self, request, pk):
        """
        Delete policy safely.
        """
        try:
            policy = get_object_or_404(IPSecPolicy, pk=pk)
            policy.delete()

            return api_response(True, "Policy deleted")

        except Exception as e:
            return api_response(False, str(e), http_status=400)
