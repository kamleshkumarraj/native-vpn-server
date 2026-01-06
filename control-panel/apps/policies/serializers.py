from rest_framework import serializers
from .models import IPSecPolicy


class IPSecPolicySerializer(serializers.ModelSerializer):
    """
    Serializer for sending IPsec policies to agent.
    Designed for control-plane → data-plane consumption.
    """

    class Meta:
        model = IPSecPolicy

        fields = (
            "id",
            "name",

            # --- IPsec mode ---
            "mode",              # ESP_TUNNEL / AH_TRANSPORT etc

            # --- Cryptographic parameters ---
            "encryption_algo",   # AES-128 / AES-256
            "integrity_algo",    # SHA1 / SHA256 / SHA384
            "dh_group",          # MODP_2048 / ECP_256
            "ike_version",       # IKEv1 / IKEv2

            # --- Traffic selection ---
            "full_tunnel",       # true = 0.0.0.0/0
            "include_subnets",   # selective encryption
            "exclude_subnets",   # bypass networks

            # --- Metadata ---
            "created_at",
        )

    def validate_include_subnets(self, value):
        """
        Ensure include_subnets is a list of CIDRs
        """
        if not isinstance(value, list):
            raise serializers.ValidationError(
                "include_subnets must be a list"
            )
        return value

    def validate_exclude_subnets(self, value):
        """
        Ensure exclude_subnets is a list of CIDRs
        """
        if not isinstance(value, list):
            raise serializers.ValidationError(
                "exclude_subnets must be a list"
            )
        return value
