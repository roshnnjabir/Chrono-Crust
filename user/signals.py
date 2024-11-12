from django.db.models.signals import pre_save
from django.core.exceptions import ValidationError
from django.dispatch import receiver
from user.models import Address
from django.db.models.signals import post_save
from .models import CustomUser
from adminapp.models import Cart, Wishlist, PersonalWallet


@receiver(pre_save, sender=Address)
def limit_address_creation(sender, instance, **kwargs):
    # Check if this is a new object (creation) by verifying if there's no primary key yet
    if instance.pk is None:  # Only run this check for newly created addresses
        if instance.user.addresses.filter(is_listed=True).count() >= 3:
            raise ValidationError("A user can only have 3 addresses.")


@receiver(post_save, sender=CustomUser)
def create_cart_for_new_user(sender, instance, created, **kwargs):
    if created:
        # Only create a cart if the user was just created
        Cart.objects.create(user=instance)
        Wishlist.objects.create(user=instance)
        PersonalWallet.objects.create(user=instance)
