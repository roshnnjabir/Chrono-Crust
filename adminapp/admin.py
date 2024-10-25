from django.contrib import admin
from .models import Brand, Collection, Product, product_slider, Cart, CartItem, Wishlist, WishlistItem
# Register your models here.


admin.site.register(Brand)
admin.site.register(Collection)
admin.site.register(Product)
admin.site.register(product_slider)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Wishlist)
admin.site.register(WishlistItem)
