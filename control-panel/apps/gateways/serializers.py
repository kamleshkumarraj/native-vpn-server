# gateways/serializers.py
from rest_framework import serializers
from .models import VPNGateway

class VPNGatewaySerializer(serializers.ModelSerializer):
    active_tunnels = serializers.IntegerField(read_only=True)

    class Meta:
        model = VPNGateway
        fields = [
            "id",
            "name",
            "public_ip",
            "hostname",
            "ike_id",
            "vpn_subnet",
            "api_endpoint",
            "is_active",
            "active_tunnels",
            "created_at"
        ]
