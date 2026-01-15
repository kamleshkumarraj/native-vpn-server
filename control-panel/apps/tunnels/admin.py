# apps/tunnels/admin.py

from django.contrib import admin
from .models import Tunnel
from django.utils.html import format_html


@admin.register(Tunnel)
class TunnelAdmin(admin.ModelAdmin):
    # Main table view
    list_display = (
        "device_name",
        "gateway",
        "status_colored",
        "virtual_ip",
        "device_public_ip",
        "bytes_in",
        "bytes_out",
        "last_seen",
        "is_active",
    )

    list_filter = (
        "status",
        "gateway",
        "is_active",
    )

    search_fields = (
        "device__hostname",
        "device__device_id",
        "virtual_ip",
        "device_public_ip",
        "connection_name",
    )

    ordering = ("-last_seen",)

    readonly_fields = (
        "connection_name",
        "ike_sa_id",
        "virtual_ip",
        "device_public_ip",
        "bytes_in",
        "bytes_out",
        "connected_at",
        "last_rekey",
        "last_seen",
        "created_at",
        "updated_at",
    )

    fieldsets = (
        ("Tunnel Identity", {
            "fields": ("device", "gateway", "connection_name", "status", "is_active")
        }),
        ("Network Information", {
            "fields": ("virtual_ip", "device_public_ip")
        }),
        ("IPsec Runtime", {
            "fields": ("ike_sa_id",)
        }),
        ("Traffic Statistics", {
            "fields": ("bytes_in", "bytes_out")
        }),
        ("Lifecycle", {
            "fields": ("connected_at", "last_rekey", "last_seen", "created_at", "updated_at")
        }),
    )

    # Disable deletion of tunnels (should be controlled by Control Plane)
    def has_delete_permission(self, request, obj=None):
        return False

    # Prevent adding tunnels manually
    def has_add_permission(self, request):
        return False

    def device_name(self, obj):
        return obj.device.hostname
    device_name.short_description = "Device"

    def status_colored(self, obj):
        colors = {
            "ESTABLISHED": "green",
            "CONNECTING": "orange",
            "REKEYING": "blue",
            "DISCONNECTED": "gray",
            "FAILED": "red",
        }
        color = colors.get(obj.status, "black")
        return format_html(
            '<b style="color:{};">{}</b>',
            color,
            obj.status
        )
    status_colored.allow_tags = True
    status_colored.short_description = "Status"
