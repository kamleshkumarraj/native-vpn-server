# apps/policies/admin.py

from django.contrib import admin
from .models import IPSecPolicy


@admin.register(IPSecPolicy)
class IPSecPolicyAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "policy_type",
        "mode",
        "tunnel_mode",
        "priority",
        "is_active",
        "assigned_tunnels",
        "created_at"
    )

    list_filter = (
        "policy_type",
        "mode",
        "full_tunnel",
        "is_active",
    )

    search_fields = ("name",)

    ordering = ("priority", "name")

    filter_horizontal = ("tunnels",)

    readonly_fields = ("created_at",)

    fieldsets = (
        ("Policy Identity", {
            "fields": ("name", "policy_type", "is_active", "priority")
        }),
        ("IPsec Mode", {
            "fields": ("mode", "ike_version")
        }),
        ("Cryptography", {
            "fields": ("encryption_algo", "integrity_algo", "dh_group")
        }),
        ("Routing Control", {
            "fields": ("full_tunnel", "include_subnets", "exclude_subnets")
        }),
        ("Tunnel Assignment (Which devices get this access)", {
            "fields": ("tunnels",)
        }),
        ("Metadata", {
            "fields": ("created_at",)
        }),
    )

    # --------- Custom columns ----------

    def assigned_tunnels(self, obj):
        return obj.tunnels.count()
    assigned_tunnels.short_description = "Devices"

    def tunnel_mode(self, obj):
        if obj.full_tunnel:
            return "Full Tunnel (0.0.0.0/0)"
        return "Split Tunnel"
    tunnel_mode.short_description = "Tunnel Mode"
