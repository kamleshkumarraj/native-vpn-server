import uuid
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ("SUPER_ADMIN", "Super Admin"),
        ("SEC_ADMIN", "Security Admin"),
        ("AUDITOR", "Auditor"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    objects = UserManager()   # 👈 VERY IMPORTANT

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []      # 👈 REQUIRED for createsuperuser

    def __str__(self):
        return self.email
