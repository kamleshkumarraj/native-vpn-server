# apps/policies/models.py
from django.db import models
class IPSecPolicy(models.Model):
    MODE_CHOICES = (
        ("ESP_TUNNEL", "ESP Tunnel"),
        ("ESP_TRANSPORT", "ESP Transport"),
        ("AH_TUNNEL", "AH Tunnel"),
        ("AH_TRANSPORT", "AH Transport"),
        ("ESP_AH", "ESP + AH"),
    )

    name = models.CharField(max_length=100, unique=True)
    mode = models.CharField(max_length=20, choices=MODE_CHOICES)

    encryption_algo = models.CharField(max_length=50)
    integrity_algo = models.CharField(max_length=50)
    dh_group = models.CharField(max_length=50)
    ike_version = models.CharField(max_length=10, default="IKEv2")

    full_tunnel = models.BooleanField(default=True)
    include_subnets = models.JSONField(default=list)
    exclude_subnets = models.JSONField(default=list)
    
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
