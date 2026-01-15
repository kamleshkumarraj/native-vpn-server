from rest_framework import serializers
from .models import IPSecPolicy


class IPSecPolicySerializer(serializers.ModelSerializer):
    """
    Serializer for sending IPsec policies to Agent.
    Control-Plane → Data-Plane.
    One tunnel receives multiple policies.
    """

    class Meta:
        model = IPSecPolicy
        fields = (
            "id",
            "name",

            # ---- Type & ordering ----
            "policy_type",
            "priority",

            # ---- IPsec mode ----
            "mode",              # ESP_TUNNEL / ESP_TRANSPORT
            "ike_version",       # IKEv2

            # ---- Cryptography ----
            "encryption_algo",
            "integrity_algo",
            "dh_group",

            # ---- Traffic Selection ----
            "full_tunnel",
            "include_subnets",
            "exclude_subnets",
        )

    # ---------------- Validators ----------------

    def validate_include_subnets(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError(
                "include_subnets must be a list of CIDR strings"
            )
        return value

    def validate_exclude_subnets(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError(
                "exclude_subnets must be a list of CIDR strings"
            )
        return value

    def validate(self, attrs):
        """
        Enforce correct split vs full tunnel logic.
        """

        if attrs.get("full_tunnel") and attrs.get("include_subnets"):
            raise serializers.ValidationError(
                "Full tunnel policies cannot have include_subnets"
            )

        if not attrs.get("full_tunnel") and not attrs.get("include_subnets"):
            raise serializers.ValidationError(
                "Split tunnel policy must have include_subnets"
            )

        return attrs
