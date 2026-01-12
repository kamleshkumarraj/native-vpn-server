from django.contrib import admin
from .models import Tunnel


@admin.register(Tunnel)
class TunnelAdmin(admin.ModelAdmin):
    """
    Admin configuration for Tunnel model.
    """

    # Columns visible in admin list view
    list_display = (
        "id",
        "device",
        "policy",
        "peer_ip",
        "local_subnet",
        "remote_subnet",
        "is_active",
        "last_rekey",
    )

    # Filters on the right sidebar
    list_filter = (
        "is_active",
        "policy",
        "device",
    )

    # Search functionality
    search_fields = (
        "peer_ip",
        "local_subnet",
        "remote_subnet",
        "device__name",
        "policy__name",
    )

    # Default ordering
    ordering = ("-last_rekey",)

    # Fields that are clickable
    list_display_links = ("id", "peer_ip")

    # Optimize ForeignKey dropdowns
    autocomplete_fields = ("device", "policy")

    # Read-only fields (system-managed)
    readonly_fields = ("last_rekey",)

    # Group fields in admin form
    fieldsets = (
        ("Tunnel Association", {
            "fields": ("device", "policy")
        }),
        ("Network Configuration", {
            "fields": ("peer_ip", "local_subnet", "remote_subnet")
        }),
        ("Status & Monitoring", {
            "fields": ("is_active", "last_rekey")
        }),
    )
