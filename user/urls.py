"""
URL configuration for crono project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.user_home, name='user_home'),
    path('user_login/', views.user_login, name='user_login'),
    path('user_signup/', views.user_signup, name='user_signup'),
    path('user_profile/', views.user_profile, name='user_profile'),
    path('user_profile_update/', views.user_profile_update, name='user_profile_update'),
    
    path('user_list_product/', views.user_list_product, name='user_list_product'),
    path('user_list_product_catogory/', views.user_list_product_catogory, name='user_list_product_catogory'),
    
    path('user_list_brand/', views.user_list_brand, name='user_list_brand'),
    path('user_list_collection/', views.user_list_collection, name='user_list_collection'),

    path('user_forgot_password/', views.user_forgot_password, name='user_forgot_password'),
    path('user_reset_password/', views.user_reset_password, name='user_reset_password'),

    path('user_profile/user_profile_image_update', views.user_profile_image_update, name='user_profile_image_update'),
    path('user_profile/personal-wallet/', views.personal_wallet, name='user_personal_wallet'),
    path('user_profile/address-book/', views.address_book, name='user_address_book'),
    path('user_profile/address-book-edit', views.edit_user_address, name='user_address_book_edit'),
    path('user_profile/address-book-add', views.add_user_address, name='add_user_address'),
    path('user_profile/delete_address/<int:address_id>', views.delete_user_address, name='delete_address'),
    path('user_profile/change-password/', views.change_password, name='user_change_password'),


    path('user_profile/user_cart_view/', views.user_cart_view, name='user_cart_view'),
    path("update-cart-item-quantity-ajax/", views.update_cart_item_quantity_ajax, name="update_cart_item_quantity_ajax"),
    path('remove_from_cart/<int:item_id>/', views.remove_from_cart, name='user_remove_from_cart'),
    path('user_profile/user_wishlist_view/', views.user_wishlist_view, name='user_wishlist_view'),
    path('user_remove_from_wishlist', views.user_remove_from_wishlist, name='user_remove_from_wishlist'),
    path('user_move_to_cart/', views.user_move_to_cart, name='user_move_to_cart'),
    path('user_profile/prepare_razorpay_payment/<str:order_id>', views.prepare_razorpay_payment, name='prepare_razorpay_payment'),
    path('user_profile/verify_razorpay_payment/', views.verify_razorpay_payment, name='verify_razorpay_payment'),
    path('user_add_to_wishlist', views.user_add_to_wishlist, name='user_add_to_wishlist'),
    path('user_move_to_wishlist/<int:item_id>', views.user_move_to_wishlist, name='user_move_to_wishlist'),
    path('user_move_to_order', views.user_move_to_order, name='user_move_to_order'),
    path('user_profile/user_order_history', views.user_order_history, name='user_order_history'),
    path('user_profile/user_order_details/<str:order_id>/', views.user_order_details, name='user_order_details'),
    path('user_order_cancel/<str:order_id>/', views.user_cancel_order, name='user_order_cancel'),
    path('address/selection/', views.address_selection, name='user_address_selection'),
    path('user_payment_method_selection/', views.user_payment_method_selection, name='user_payment_method_selection'),  # after payment is made...redirect to move to order...
    path('user_logout/', views.user_logout, name='user_logout'),

    path('otp_page', views.otp_page, name='otp_page'),
    path('verify_otp', views.verify_otp, name='verify_otp'),
    path('resend_otp', views.resend_otp, name='resend_otp'),

    path('view_product/<int:id>', views.view_product, name='view_product'),
    path('view_brand/<int:id>', views.view_brand, name='view_brand'),
    path('view_collection/<int:id>', views.view_collection, name='view_collection'),
    path('user_add_to_cart/', views.user_add_to_cart, name='user_add_to_cart'),
    
    path('validate-coupon/', views.validate_coupon_ajax, name='validate_coupon_ajax'),

    path('user_profile/add_money_to_wallet/', views.add_money_to_wallet, name='add_money_to_wallet'),
    
    
    path('user_generate_invoice/<str:order_id>', views.user_generate_invoice, name='user_generate_invoice')
]
