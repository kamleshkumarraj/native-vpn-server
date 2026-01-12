from django.contrib import admin
from .models import Certificate


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    """
    Admin configuration for Certificates.
    """

    list_display = (
        "id",
        "device",
        "cert_type",
        "serial_number",
        "fingerprint",
        "issued_at",
        "expires_at",
        "revoked",
    )

    list_filter = (
        "cert_type",
        "revoked",
        "issued_at",
        "expires_at",
    )

    search_fields = (
        "serial_number",
        "fingerprint",
        "device__name",
    )

    ordering = ("-issued_at",)

    readonly_fields = ("issued_at",)

    list_display_links = ("serial_number",)

    autocomplete_fields = ("device",)

    fieldsets = (
        ("Certificate Identity", {
            "fields": ("cert_type", "serial_number", "fingerprint")
        }),
        ("Association", {
            "fields": ("device",)
        }),
        ("Validity", {
            "fields": ("issued_at", "expires_at", "revoked")
        }),
    )
