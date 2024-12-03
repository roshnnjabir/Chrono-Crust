from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from .managers import CustomUserManager


# Create your models here.
class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(_("email address"), unique=True)
    date_of_birth = models.DateField(null=True)
    phone = models.CharField()
    profile_image = models.ImageField(upload_to='uploads/profile', null=True)

    THEME_CHOICES = [
        ('dark', 'Dark'),
        ('light', 'Light'),
    ]
    theme = models.CharField(max_length=5, choices=THEME_CHOICES, default='light')

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def get_full_name(self):
        # If first and last name are not provided, return email
        return self.first_name + " " + self.last_name if self.first_name and self.last_name else self.email

    def __str__(self):
        return self.email


class Address(models.Model):
    user = models.ForeignKey(CustomUser, related_name="addresses", on_delete=models.CASCADE)
    building_name = models.CharField(max_length=100)
    landmark = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    phone = models.CharField()
    is_listed = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.building_name}, {self.city}, {self.country}"
