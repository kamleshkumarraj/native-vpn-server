from django.contrib import admin
from .models import VPNGateway
from apps.tunnels.models import Tunnel


@admin.register(VPNGateway)
class VPNGatewayAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "public_ip",
        "ike_id",
        "vpn_subnet",
        "is_active",
        "active_tunnels",
        "created_at",
    )

    list_filter = (
        "is_active",
    )

    search_fields = (
        "name",
        "public_ip",
        "hostname",
        "ike_id",
    )

    ordering = ("name",)

    readonly_fields = (
        "created_at",
    )

    fieldsets = (
        ("Gateway Identity", {
            "fields": ("name", "public_ip", "hostname", "ike_id")
        }),
        ("VPN Configuration", {
            "fields": ("vpn_subnet", "api_endpoint")
        }),
        ("Operational State", {
            "fields": ("is_active",)
        }),
        ("Metadata", {
            "fields": ("created_at",)
        }),
    )

    # --------------------------
    # Custom Columns
    # --------------------------

    def active_tunnels(self, obj):
        """
        Shows how many device tunnels are connected to this gateway.
        """
        return Tunnel.objects.filter(
            gateway=obj,
            status="ESTABLISHED",
            is_active=True
        ).count()

    active_tunnels.short_description = "Active Devices"

    # --------------------------
    # Safety Rules
    # --------------------------

    def has_delete_permission(self, request, obj=None):
        """
        Prevent deleting a gateway that has active tunnels.
        """
        if obj and Tunnel.objects.filter(gateway=obj).exists():
            return False
        return True
