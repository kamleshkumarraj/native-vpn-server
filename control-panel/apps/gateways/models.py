from django.db import models

class VPNGateway(models.Model):
    name = models.CharField(max_length=100)
    public_ip = models.GenericIPAddressField()
    hostname = models.CharField(max_length=255, null=True, blank=True)

    # IKE identity used by strongSwan (leftid)
    ike_id = models.CharField(max_length=255)

    # Subnet used to assign virtual IPs to devices
    vpn_subnet = models.CharField(max_length=64)   # e.g. 10.10.10.0/24

    # strongSwan API or control socket (future use)
    api_endpoint = models.URLField(null=True, blank=True)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.public_ip})"

