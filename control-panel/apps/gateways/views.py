from django.shortcuts import render

# Create your views here.
# gateways/views.py
from rest_framework import viewsets, status
from rest_framework.response import Response
from django.db.models import Count, Q
from .models import VPNGateway
from .serializers import VPNGatewaySerializer
from tunnels.models import Tunnel

class VPNGatewayViewSet(viewsets.ModelViewSet):
    queryset = VPNGateway.objects.all()
    serializer_class = VPNGatewaySerializer

    def get_queryset(self):
        return VPNGateway.objects.annotate(
            active_tunnels=Count(
                "tunnels",
                filter=Q(tunnels__status="ESTABLISHED")
            )
        )

    def destroy(self, request, *args, **kwargs):
        gateway = self.get_object()

        # Prevent deleting a gateway if tunnels exist
        if Tunnel.objects.filter(gateway=gateway, is_active=True).exists():
            return Response(
                {"error": "Cannot delete gateway with active tunnels"},
                status=status.HTTP_400_BAD_REQUEST
            )

        return super().destroy(request, *args, **kwargs)
