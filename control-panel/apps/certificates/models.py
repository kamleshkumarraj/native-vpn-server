# apps/certificates/models.py
from django.db import models
import uuid
class Certificate(models.Model):
    CERT_TYPE = (
        ("DEVICE", "Device"),
        ("IKE", "IKE"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    device = models.ForeignKey(
    "devices.Device",
    on_delete=models.CASCADE,
    null=True,
    blank=True,
    related_name="certificates"
    )

    cert_type = models.CharField(max_length=20, choices=CERT_TYPE)
    serial_number = models.CharField(max_length=64, unique=True)
    fingerprint = models.CharField(max_length=128)
    issued_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    revoked = models.BooleanField(default=False)
