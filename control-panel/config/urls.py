# control_plane/urls.py
from django.urls import path

from apps.devices.views import DeviceRegisterView
from apps.certificates.views import CertificateSignView
from apps.policies.views import PolicyView
from apps.tunnels.views import TunnelView
from apps.telemetry.views import HeartbeatView, StatusView
from apps.accounts.views import RegisterView, LoginView

urlpatterns = [
    path("api/devices/register/", DeviceRegisterView.as_view()),
    path("api/certificates/sign/", CertificateSignView.as_view()),
    path("api/policies/", PolicyView.as_view()),
    path("api/policies/<uuid:pk>/", PolicyView.as_view()),
    path("api/tunnels/", TunnelView.as_view()),
    path("api/telemetry/heartbeat/", HeartbeatView.as_view()),
    path("api/telemetry/status/", StatusView.as_view()),
    path("api/auth/register/", RegisterView.as_view()),
    path("api/auth/login/", LoginView.as_view()),
    
]
