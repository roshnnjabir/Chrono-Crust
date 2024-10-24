from django.db.models.signals import pre_save
from django.core.exceptions import ValidationError
from django.dispatch import receiver
from user.models import Address


@receiver(pre_save, sender=Address)
def limit_address_creation(sender, instance, **kwargs):
    # Check if this is a new object (creation) by verifying if there's no primary key yet
    if instance.pk is None:  # Only run this check for newly created addresses
        if instance.user.addresses.count() >= 3:
            raise ValidationError("A user can only have 3 addresses.")
