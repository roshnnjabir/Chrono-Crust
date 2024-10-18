from django.db import models


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
    description = models.CharField(max_length=500, default='', blank=True, null=True)
    stock = models.CharField(max_length=3)
    image = models.ImageField(upload_to='uploads/product')
    image1 = models.ImageField(upload_to='uploads/product')
    image2 = models.ImageField(upload_to='uploads/product')
    is_listed = models.BooleanField(default=True)
    video_path = models.CharField(max_length=500, blank=True, null=True)

    def __str__(self):
        return self.name
