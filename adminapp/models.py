from django.db import models
from user.models import CustomUser, Address
from django.db.models import Sum, F
from decimal import Decimal
from django.utils import timezone


class Brand(models.Model):
    name = models.CharField(max_length=50)
    logo_image = models.ImageField(upload_to='uploads/brands/logo')
    banner_image = models.ImageField(upload_to='uploads/brands/banner')
    discription = models.TextField(max_length=50, null=True, blank=True)
    is_listed = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Collection(models.Model):
    name = models.CharField(max_length=50)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, default=1)
    image = models.ImageField(upload_to='uploads/collection')
    is_listed = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Product(models.Model):
    reference_no = models.CharField(max_length=50)
    name = models.CharField(max_length=50)

    price = models.DecimalField(default=0, decimal_places=3, max_digits=9)
    offer_price = models.DecimalField(default=0, decimal_places=3, max_digits=9)

    collection = models.ForeignKey(Collection, on_delete=models.CASCADE, default=1)

    description = models.CharField(max_length=500, default='', blank=True, null=True)
    description1 = models.CharField(max_length=500, default='', blank=True, null=True)
    description1header = models.CharField(max_length=500, default='', blank=True, null=True)
    description2 = models.CharField(max_length=1000, default='', blank=True, null=True)

    stock = models.PositiveIntegerField()

    image = models.FileField(upload_to='uploads/product')
    image1 = models.ImageField(upload_to='uploads/product')
    image2 = models.ImageField(upload_to='uploads/product')
    image3 = models.ImageField(upload_to='uploads/product')

    is_listed = models.BooleanField(default=False)

    diameter = models.IntegerField(default=42)
    frequency = models.IntegerField(default=3600)  # Corrected spelling from 'frequency'
    power_reserve = models.IntegerField(default=60)
    water_resistance = models.IntegerField(default=10)

    limited_edition = models.BooleanField(default=False)

    popularity = models.IntegerField(default=0)  # If you want to track popularity

    created_at = models.DateTimeField(auto_now_add=True)  # Automatically set when created

    for_men = models.BooleanField(default=True)
    for_women = models.BooleanField(default=True)

    def save(self, *args, **kwargs):  # if no offer price then set the offer price to total price
        if self.offer_price == 0:
            self.offer_price = self.price  # set default, i.e offer price to price if there is no offer(i,e offer=0[default])

        # Call the parent class's save method to save the instance to the database
        super().save(*args, **kwargs)

    def get_discounted_price(self):
        now = timezone.now()
        product_offer = Offer.objects.filter(
            applicable_products=self,
            start_date__lte=now,
            end_date__gte=now,
        ).first()
        
        collection_offer = Offer.objects.filter(
            applicable_collections=self.collection,
            start_date__lte=now,
            end_date__gte=now,
        ).first()
        
        brand_offer = Offer.objects.filter(
            applicable_brands=self.collection.brand,  # Assuming Collection has a brand field
            start_date__lte=now,
            end_date__gte=now,
        ).first()

        # Determine which offers are available
        applicable_offers = [offer for offer in [product_offer, collection_offer, brand_offer] if offer]
        if not applicable_offers:
            return self.price  # No active offers, return original price

        # Apply the offers by summing up discounts
        total_discount = Decimal(0)
        for offer in applicable_offers:
            if offer.discount_type == 'percentage':
                discount = (self.price * offer.discount_amount) / Decimal(100)
            else:
                discount = offer.discount_amount
            total_discount += discount

        # Ensure final price isn't below zero
        discounted_price = max(self.price - total_discount, Decimal(0))
        return discounted_price

    def get_discount_percentage(self):
        discounted_price = self.get_discounted_price()
        if discounted_price < self.price:
            discount_percentage = ((self.price - discounted_price) / self.price) * 100
            return round(discount_percentage, 2)  # Round to two decimal places
        return 0  # No discount


    def __str__(self):
        return self.name


class Product_Slider(models.Model):
    collection = models.OneToOneField(Collection, on_delete=models.CASCADE, default=1)
    description = models.CharField(max_length=500)

    def __str__(self):
        return self.collection.name


class Cart(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)

    def __str__(self):
        return f"Cart of {self.user}"

    @property
    def total_price(self):
        # Calculate the total price by summing product prices times quantities for all items in the cart
        return self.items.aggregate(total=Sum(F('product__offer_price') * F('quantity')))['total'] or 0.0


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in cart of {self.cart.user}"

    @property
    def total_price(self):
        # Calculate the total price for this cart item
        return self.product.offer_price * Decimal(self.quantity)


class Wishlist(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)

    def __str__(self):
        return f"Wishlist of {self.user}"


class WishlistItem(models.Model):
    wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('wishlist', 'product')

    def __str__(self):
        return f"{self.product.name} in wishlist of {self.wishlist.user}"


class Order(models.Model):
    id = models.CharField(primary_key=True, auto_created=True, max_length=20)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="orders")
    payment_id = models.CharField(max_length=20)
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('cod', 'Cod'),
        ('paid', 'Paid'),
        ('refunded', 'Refunded'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=8, choices=PAYMENT_STATUS_CHOICES, default='pending')

    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    discounted_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        # if no discount, the discount price default should be total_amount itself
        if self.discounted_amount == 0:
            self.discounted_amount = self.total_amount
        # calling the save of parent class
        super().save(*args, **kwargs)

    # def calculate_total(self):
    #     total = sum(item.price for item in self.items.all())
    #     self.total_amount = total
    #     self.save()

    def __str__(self):
        return f"Order #{self.id} by {self.user.email} on {self.created_at} - Status: {self.status}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)  # Assuming you have a Product model
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Store price to prevent changes in the product's price affecting past orders

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Order #{self.order.id}"


class PersonalWallet(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.PROTECT)
    balance = models.IntegerField(default=0)


class PersonalWalletTransactions(models.Model):
    personal_wallet = models.ForeignKey(PersonalWallet, on_delete=models.PROTECT, related_name="items")
    created_at = models.DateTimeField(auto_now_add=True)
    method_choices = [
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
        ('debited', 'Debited'),
        ('credited', 'Credited')
    ]
    method = models.CharField(choices=method_choices, default='cancelled')


class Coupen(models.Model):
    code = models.CharField(max_length=10, unique=True)
    min_required = models.IntegerField(default=10000)
    maximum_discount = models.IntegerField(default=1000)
    discount_percentage = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    active = models.BooleanField(default=False)
    usage_limit = models.IntegerField(default=3)
    used_count = models.PositiveIntegerField(default=0)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()

    def __str__(self):
        return self.code


class Offer(models.Model):
    OFFER_TYPE_CHOICES = [
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
    ]

    name = models.CharField(max_length=100)
    discount_type = models.CharField(max_length=10, choices=OFFER_TYPE_CHOICES)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    
    # Allow only one of these to be populated at a time
    applicable_products = models.ManyToManyField(Product, blank=True)
    applicable_collections = models.ManyToManyField(Collection, blank=True)
    applicable_brands = models.ManyToManyField(Brand, blank=True)

    def clean(self):
        # Check that only one of the fields is populated
        selected_types = sum(bool(getattr(self, field).exists()) for field in ['applicable_products', 'applicable_collections', 'applicable_brands'])
        if selected_types > 1:
            raise ValidationError("Only one of applicable_products, applicable_collections, or applicable_brands can be set.")

    def is_active(self):
        now = timezone.now()
        return self.start_date <= now <= self.end_date

    def __str__(self):
        return self.name