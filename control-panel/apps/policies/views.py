from django.shortcuts import render

# Create your views here.
# apps/policies/views.py
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .models import IPSecPolicy
from apps.common.utils.response import api_response
from .serializers import IPSecPolicySerializer


class PolicyView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            device = request.user   # device from certificate

            policies = IPSecPolicy.objects.filter(is_active=True)

            serializer = IPSecPolicySerializer(policies, many=True)

            return api_response(
                True,
                "Policies fetched successfully",
                serializer.data,
                status.HTTP_200_OK
            )

        except Exception as e:
            return api_response(
                False,
                f"Failed to fetch policies: {str(e)}",
                http_status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def post(self, request):
        try:
            policy = IPSecPolicy.objects.create(**request.data)
            return api_response(True, "Policy created", {"id": policy.id})
        except Exception as e:
            return api_response(False, str(e), http_status=400)

    def put(self, request, pk):
        try:
            policy = IPSecPolicy.objects.get(pk=pk)
            for key, value in request.data.items():
                setattr(policy, key, value)
            policy.save()
            return api_response(True, "Policy updated")
        except IPSecPolicy.DoesNotExist:
            return api_response(False, "Policy not found", http_status=404)
        except Exception as e:
            return api_response(False, str(e), http_status=400)

    def delete(self, request, pk):
        try:
            IPSecPolicy.objects.get(pk=pk).delete()
            return api_response(True, "Policy deleted")
        except Exception as e:
            return api_response(False, str(e), http_status=400)
