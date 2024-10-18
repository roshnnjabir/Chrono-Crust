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
    
    path('upload_cropped_image/', views.upload_cropped_image, name='upload_cropped_image'),
] 
