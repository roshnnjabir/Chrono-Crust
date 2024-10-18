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
from . import views

urlpatterns = [
    path('', views.user_home, name='user_home'),
    path('user_login/', views.user_login, name='user_login'),
    path('user_signup/', views.user_signup, name='user_signup'),
    path('user_profile/', views.user_profile, name='user_profile'),
    path('user_profile_update/', views.user_profile_update, name='user_profile_update'),
    path('user_logout/', views.user_logout, name='user_logout'),

    path('otp_page', views.otp_page, name='otp_page'),
    path('verify_otp', views.verify_otp, name='verify_otp'),
    path('resend_otp', views.resend_otp, name='resend_otp'),
    
    path('view_product/<int:id>', views.view_product, name='view_product'),
]
