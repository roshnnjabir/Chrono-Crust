from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator

from .managers import CustomUserManager


# Create your models here.
class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(_("email address"), unique=True)
    date_of_birth = models.DateField(null=True)
    phone = models.CharField()
    address = models.TextField(max_length=50, null=True, blank=True)
    otp = models.CharField(max_length=6, null=True, blank=True)
    otp_expiry = models.DateTimeField(blank=True, null=True)
    max_otp_try = models.CharField(max_length=2, default=3)
    otp_max_out = models.DateTimeField(blank=True, null=True)
    profile_image = models.ImageField(upload_to='uploads/profile', null=True)

    THEME_CHOICES = [
        ('dark', 'Dark'),
        ('light', 'Light'),
    ]
    theme = models.CharField(max_length=5, choices=THEME_CHOICES, default='light')

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email
