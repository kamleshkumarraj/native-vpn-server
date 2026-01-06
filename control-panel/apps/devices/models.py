# apps/devices/models.py
import uuid
from django.db import models

class Device(models.Model):
    OS_CHOICES = (
        ("LINUX", "Linux"),
        ("WINDOWS", "Windows"),
        ("MACOS", "macOS"),
        ("BOSS", "BOSS"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    hostname = models.CharField(max_length=255)
    os_type = models.CharField(max_length=20, choices=OS_CHOICES)
    os_version = models.CharField(max_length=50)
    ip_address = models.GenericIPAddressField()
    agent_version = models.CharField(max_length=20)

    certificate_fingerprint = models.CharField(max_length=128, unique=True)
    is_active = models.BooleanField(default=True)
    last_seen = models.DateTimeField(null=True)

    created_at = models.DateTimeField(auto_now_add=True)
