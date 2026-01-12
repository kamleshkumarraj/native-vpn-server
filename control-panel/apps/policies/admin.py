from django.contrib import admin
from .models import IPSecPolicy


@admin.register(IPSecPolicy)
class IPSecPolicyAdmin(admin.ModelAdmin):
    """
    Admin configuration for IPSec Policy.
    """

    list_display = (
        "name",
        "mode",
        "encryption_algo",
        "integrity_algo",
        "dh_group",
        "ike_version",
        "full_tunnel",
        "is_active",
        "created_at",
    )

    list_filter = (
        "mode",
        "ike_version",
        "full_tunnel",
        "is_active",
    )

    search_fields = (
        "name",
        "encryption_algo",
        "integrity_algo",
        "dh_group",
    )

    ordering = ("-created_at",)

    readonly_fields = ("created_at",)

    list_display_links = ("name",)

    fieldsets = (
        ("Basic Policy Info", {
            "fields": ("name", "mode", "is_active")
        }),
        ("Cryptographic Settings", {
            "fields": (
                "encryption_algo",
                "integrity_algo",
                "dh_group",
                "ike_version",
            )
        }),
        ("Tunnel Behavior", {
            "fields": ("full_tunnel",)
        }),
        ("Traffic Selectors", {
            "fields": ("include_subnets", "exclude_subnets"),
            "description": "Define which subnets are included/excluded in IPSec"
        }),
        ("Metadata", {
            "fields": ("created_at",)
        }),
    )
