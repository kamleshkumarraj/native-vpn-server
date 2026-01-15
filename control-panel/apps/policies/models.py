# apps/policies/models.py
from django.db import models

class IPSecPolicy(models.Model):

    POLICY_TYPE_CHOICES = (
        ("SITE", "Site to Site"),
        ("REMOTE_ACCESS", "Remote Access"),
    )

    MODE_CHOICES = (
        ("ESP_TUNNEL", "ESP Tunnel"),
        ("ESP_TRANSPORT", "ESP Transport"),
    )

    name = models.CharField(max_length=100, unique=True)

    # What type of VPN this policy is
    policy_type = models.CharField(max_length=20, choices=POLICY_TYPE_CHOICES, default="REMOTE_ACCESS")

    # IPsec mode
    mode = models.CharField(max_length=20, choices=MODE_CHOICES, default="ESP_TUNNEL")

    # Cryptography
    encryption_algo = models.CharField(max_length=50, default="aes256")
    integrity_algo = models.CharField(max_length=50, default="sha256")
    dh_group = models.CharField(max_length=50, default="modp2048")
    ike_version = models.CharField(max_length=10, default="IKEv2")

    # Routing
    full_tunnel = models.BooleanField(default=False)
    include_subnets = models.JSONField(default=list)   # Traffic Selectors (TSr)
    exclude_subnets = models.JSONField(default=list)

    # Used when multiple policies exist
    priority = models.IntegerField(default=100)

    # Many-to-Many: One tunnel has many policies
    tunnels = models.ManyToManyField(
        "tunnels.Tunnel",
        related_name="policies",
        blank=True
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
