from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from cryptography.fernet import Fernet
import json

cipher = Fernet(settings.ENCRYPTION_KEY)


class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, **extra_fields):
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    otp_secret = models.CharField(max_length=64, blank=True, null=True)
    recovery_codes = models.TextField(null=True, blank=True)
    otp_activated = models.BooleanField(default=True)
    otp_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def generate_recovery_codes(self):
        recovery_codes = [User.objects.make_random_password() for _ in range(10)]
        encrypted_codes = cipher.encrypt(json.dumps(recovery_codes).encode())
        self.recovery_codes = encrypted_codes.decode()
        self.save()
        return recovery_codes

    def verify_recovery_code(self, code):
        if self.recovery_codes:
            decrypted_codes = cipher.decrypt(self.recovery_codes.encode()).decode()
            recovery_codes = json.loads(decrypted_codes)

            if code in recovery_codes:
                recovery_codes.remove(code)
                self.recovery_codes = cipher.encrypt(json.dumps(recovery_codes).encode()).decode()
                self.save()
                return True

        return False
