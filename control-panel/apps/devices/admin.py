from django.contrib import admin
from .models import Device


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    """
    Admin configuration for Device model.
    Required for autocomplete_fields used in
    TunnelAdmin and CertificateAdmin.
    """

    # Columns shown in list view
    list_display = (
        "hostname",
        "ip_address",
        "os_type",
        "os_version",
        "agent_version",
        "is_active",
        "last_seen",
        "created_at",
    )

    # Right-side filters
    list_filter = (
        "os_type",
        "is_active",
        "created_at",
    )

    # REQUIRED for autocomplete_fields
    search_fields = (
        "hostname",
        "ip_address",
        "certificate_fingerprint",
    )

    # Default ordering
    ordering = ("-last_seen",)

    # Clickable column
    list_display_links = ("hostname",)

    # Read-only system fields
    readonly_fields = (
        "id",
        "created_at",
        "last_seen",
    )

    # Better form layout
    fieldsets = (
        ("Device Identity", {
            "fields": (
                "id",
                "hostname",
                "ip_address",
            )
        }),
        ("Operating System", {
            "fields": (
                "os_type",
                "os_version",
                "agent_version",
            )
        }),
        ("Security", {
            "fields": (
                "certificate_fingerprint",
            )
        }),
        ("Status & Monitoring", {
            "fields": (
                "is_active",
                "last_seen",
                "created_at",
            )
        }),
    )
