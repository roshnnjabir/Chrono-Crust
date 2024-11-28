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
from django.contrib import admin
from django.urls import path
from adminapp import views

urlpatterns = [
    path('admin/', views.admin, name='admin'),
    path('admin_logout/', views.admin_logout, name='admin_logout'),
    path('admin_login/', views.admin_login, name='admin_login'),
    path('admin/list_user/', views.admin_list_user, name='admin_list_user'),
    path('admin/show_user_details/<int:id>', views.admin_show_user_details, name='admin_show_user_details'),
    path('admin/show_order_of_specific_user/<int:id>', views.admin_show_order_of_specific_user, name='show_order_of_specific_user'),
    path('admin/blocked_users', views.admin_list_blocked_user, name='admin_list_blocked_user'),
    path('admin/block_unblock/<int:id>', views.admin_block_unblock_user, name="block_unblock_user"),

    path('admin/list_product/', views.admin_list_product, name='admin_list_product'),
    path('admin/add_product/', views.admin_add_product, name='admin_add_product'),
    path('admin/list_unlist_product/<int:id>', views.admin_list_unlist_product, name='admin_list_unlist_product'),
    path('admin/edit_product/<int:id>', views.admin_edit_product, name='admin_edit_product'),
    path('admin/delete_product/<int:id>', views.admin_delete_product, name='admin_delete_product'),


    path('admin/list_collection', views.admin_list_collection, name='admin_list_collection'),
    path('admin/add_collection/', views.admin_add_collection, name='admin_add_collection'),
    path('admin/list_unlist_collection/<int:id>', views.admin_list_unlist_collection, name='admin_list_unlist_collection'),
    path('admin/edit_collection/<int:id>', views.admin_edit_collection, name='admin_edit_collection'),
    path('admin/delete_collection/<int:id>', views.admin_delete_collection, name='admin_delete_collection'),


    path('admin/list_brand', views.admin_list_brand, name='admin_list_brand'),
    path('admin/add_brand/', views.admin_add_brand, name='admin_add_brand'),
    path('admin/list_unlist_brand/<int:id>', views.admin_list_unlist_brand, name='admin_list_unlist_brand'),
    path('admin/edit_brand/<int:id>', views.admin_edit_brand, name='admin_edit_brand'),
    path('admin/delete_brand/<int:id>', views.admin_delete_brand, name='admin_delete_brand'),


    path('admin/orders', views.admin_list_orders, name='admin_list_orders'),
    path('admin/order/<str:order_id>/', views.admin_order_details, name='admin_order_details'),
    path('admin/update_order_status/<str:order_id>/', views.update_order_status, name='update_order_status'),
    path('admin/update_payment_status/<str:order_id>/', views.update_payment_status, name='update_payment_status'),
    
    path('admin/list_coupons', views.admin_coupons, name='admin_list_coupons'),
    # path('admin/coupon_details/<str:code>', views.admin_coupon_details, name="admin_coupon_details"), # commmnted cause no use now, add later
    path('admin/delete_coupon/<str:code>', views.admin_delete_coupon, name="admin_delete_coupon"),
    path('admin/add_coupon/', views.admin_add_coupon, name='admin_add_coupon'),
    path('admin/edit_coupon/<int:coupon_id>', views.admin_edit_coupon, name='admin_edit_coupon'),
    
    path('admin/sales', views.admin_sales, name='admin_sales'),
    
    path('admin/offers', views.admin_list_offers, name='admin_offers'),
    path('admin/add_offer', views.admin_add_offers, name='admin_add_offer'),
    path('admin/delete_offer/<int:id>', views.admin_delete_offer, name='admin_delete_offer'),


    path('upload_cropped_image/', views.upload_cropped_image, name='upload_cropped_image'),
]
