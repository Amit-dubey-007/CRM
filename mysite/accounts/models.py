from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from .manager import UserManager

class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True)
    dob = models.DateField(null=True, blank=True)

    profile_image = models.ImageField(
        upload_to="profiles/",
        blank=True,
        null=True
    )

    is_email_verified = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []


class EmailOTP(models.Model):
    REGISTER = "register"
    RESET = "reset"

    PURPOSE_CHOICES = [
        (REGISTER, "Register"),
        (RESET, "Reset Password"),
    ]
    password = models.CharField(max_length=128)
    email = models.EmailField(unique=True)
    otp = models.CharField(max_length=6)
    purpose = models.CharField(max_length=20, choices=PURPOSE_CHOICES)
    created_at = models.DateTimeField(auto_now=True)
    resend_count = models.IntegerField(default=0)
    last_resend_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.email} - {self.otp}"
    
    def is_expired(self):
        expiration_time = self.created_at + timezone.timedelta(minutes=5)
        return timezone.now() > expiration_time
    
    def can_resend(self):
        if self.last_resend_time + timezone.timedelta(seconds=30) > timezone.now():
            return False
        return True
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["email", "purpose"],
                name="unique_email_purpose"
            )
        ]
    