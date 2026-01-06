from django.db import models

# Create your models here.
# apps/tunnels/models.py
class Tunnel(models.Model):
    device = models.ForeignKey("devices.Device", on_delete=models.CASCADE)
    policy = models.ForeignKey("policies.IPSecPolicy", on_delete=models.CASCADE)

    local_subnet = models.CharField(max_length=64)
    remote_subnet = models.CharField(max_length=64)
    peer_ip = models.GenericIPAddressField()

    is_active = models.BooleanField(default=False)
    last_rekey = models.DateTimeField(null=True)
