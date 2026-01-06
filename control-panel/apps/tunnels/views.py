from django.shortcuts import render

# Create your views here.
# apps/tunnels/views.py
from rest_framework.views import APIView
from rest_framework import status

from .models import Tunnel
from apps.common.utils.response import api_response
from apps.devices.models import Device
from apps.policies.models import IPSecPolicy

class TunnelView(APIView):

    def get(self, request):
        try:
            tunnels = Tunnel.objects.all().values()
            return api_response(True, "Tunnels fetched", list(tunnels))
        except Exception as e:
            return api_response(False, str(e), http_status=500)

    def post(self, request):
        try:
            device = Device.objects.filter(pk=request.data["device_id"]).first()
            request.data["device"] = device
            policy = IPSecPolicy.objects.filter(pk=request.data["policy_id"]).first()
            request.data["policy"] = policy
            tunnel = Tunnel.objects.create(**request.data)
            
            return api_response(
                True,
                "Tunnel created",
                {"tunnel_id": tunnel.id},
                status.HTTP_201_CREATED
            )
        except Exception as e:
            return api_response(False, str(e), http_status=400)
