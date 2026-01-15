from django.db import models

# Create your models here.
# apps/tunnels/models.py

class Tunnel(models.Model):
    """
    Represents a single IKEv2/IPsec VPN tunnel.
    Exactly ONE tunnel exists per Device.
    """

    device = models.OneToOneField(
        "devices.Device",
        on_delete=models.CASCADE,
        related_name="tunnel"
    )

    # VPN Gateway this tunnel is connected to
    gateway = models.ForeignKey(
        "gateways.VPNGateway",
        on_delete=models.CASCADE,
        related_name="tunnels"
    )

    # IKE / IPsec runtime identifiers
    ike_sa_id = models.CharField(max_length=128, null=True, blank=True)
    connection_name = models.CharField(max_length=128, unique=True)

    # Virtual IP assigned to device inside VPN
    virtual_ip = models.GenericIPAddressField(null=True, blank=True)

    # Public IP of device (outside VPN)
    device_public_ip = models.GenericIPAddressField(null=True, blank=True)

    # Current tunnel state
    status = models.CharField(
        max_length=32,
        choices=[
            ("DISCONNECTED", "Disconnected"),
            ("CONNECTING", "Connecting"),
            ("ESTABLISHED", "Established"),
            ("REKEYING", "Rekeying"),
            ("FAILED", "Failed"),
        ],
        default="DISCONNECTED"
    )

    # Traffic stats
    bytes_in = models.BigIntegerField(default=0)
    bytes_out = models.BigIntegerField(default=0)

    # Lifecycle tracking
    connected_at = models.DateTimeField(null=True, blank=True)
    last_rekey = models.DateTimeField(null=True, blank=True)
    last_seen = models.DateTimeField(null=True, blank=True)

    # Health
    is_active = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.device.hostname} → {self.gateway.name} ({self.status})"

