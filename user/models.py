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

    def __str__(self):
        return self.email


class Address(models.Model):
    user = models.ForeignKey(CustomUser, related_name="addresses", on_delete=models.CASCADE)
    street_address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    is_default = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # If the instance has a primary key, it means we're updating an existing address
        if not self.pk and self.user.addresses.count() >= 3:
            raise ValidationError("A user can only have 3 addresses.")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.street_address}, {self.city}, {self.country}"
