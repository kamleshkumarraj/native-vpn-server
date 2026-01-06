from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework import status
from django.contrib.auth import get_user_model
from apps.common.utils.response import api_response

User = get_user_model()


class RegisterView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        try:
            email = request.data["email"]
            password = request.data["password"]
            role = request.data.get("role", "SEC_ADMIN")

            if User.objects.filter(email=email).exists():
                return api_response(False, "User already exists", http_status=400)

            user = User.objects.create_user(
                email=email,
                password=password,
                role=role
            )

            return api_response(True, "User registered successfully")

        except Exception as e:
            return api_response(False, str(e), http_status=500)


from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

class LoginView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        user = authenticate(
            email=request.data["email"],
            password=request.data["password"]
        )

        if not user:
            return api_response(False, "Invalid credentials", http_status=401)

        refresh = RefreshToken.for_user(user)

        return api_response(
            True,
            "Login successful",
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh)
            }
        )
