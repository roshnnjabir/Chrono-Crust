from django.db import models
from user.models import CustomUser


class Brand(models.Model):
    name = models.CharField(max_length=50)
    is_listed = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Collection(models.Model):
    name = models.CharField(max_length=50)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, default=1)
    is_listed = models.BooleanField(default=True)

    def __str__(self):
        return self.name


# Create your models here.
class Product(models.Model):
    name = models.CharField(max_length=50)
    price = models.DecimalField(default=0, decimal_places=3, max_digits=9)
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE, default=1)
    description = models.CharField(max_length=500, default='', blank=True, null=True)
    description1 = models.CharField(max_length=500, default='', blank=True, null=True)
    description2 = models.CharField(max_length=1000, default='', blank=True, null=True)
    stock = models.CharField(max_length=3)
    image = models.ImageField(upload_to='uploads/product')
    image1 = models.ImageField(upload_to='uploads/product')
    image2 = models.ImageField(upload_to='uploads/product')
    is_listed = models.BooleanField(default=True)
    diameter = models.IntegerField(default=42)
    freequency = models.IntegerField(default=3600)
    power_reserve = models.IntegerField(default=60)
    water_resistance = models.IntegerField(default=10)

    def __str__(self):
        return self.name


class product_slider(models.Model):
    name = models.CharField(max_length=50)
    product = models.OneToOneField(Product, on_delete=models.CASCADE, default=1)
    description = models.CharField(max_length=500)


class Cart(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)

    def __str__(self):
        return f"Cart of {self.user}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in cart of {self.cart.user}"


class Wishlist(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)

    def __str__(self):
        return f"Wishlist of {self.user}"


class WishlistItem(models.Model):
    wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.product.name} in wishlist of {self.wishlist.user}"
