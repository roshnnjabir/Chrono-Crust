from django.contrib import admin
from .models import Brand, Collection, Product, Product_Slider, Cart, CartItem, Wishlist, WishlistItem, Order, OrderItem, PersonalWallet, PersonalWalletTransactions, Coupen
# Register your models here.


admin.site.register(Brand)
admin.site.register(Collection)
admin.site.register(Product)
admin.site.register(Product_Slider)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Wishlist)
admin.site.register(WishlistItem)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(PersonalWallet)
admin.site.register(PersonalWalletTransactions)
admin.site.register(Coupen)
