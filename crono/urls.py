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
from django.urls import path, include
from . import settings
from django.conf.urls.static import static
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from django.shortcuts import redirect
from allauth.socialaccount.models import SocialApp


def direct_google_login(request):
    try:
        social_app = SocialApp.objects.get(provider='google')

        authorization_url = 'https://accounts.google.com/o/oauth2/v2/auth'

        redirect_uri = request.build_absolute_uri('/accounts/google/login/callback/')

        params = {
            'client_id': social_app.client_id,
            'response_type': 'code',
            'scope': 'openid email profile',
            'redirect_uri': redirect_uri,
            'state': 'random_state_to_prevent_csrf',  # Optional but recommended
        }

        # Create full URL with parameters
        full_url = f"{authorization_url}?{'&'.join(f'{k}={v}' for k, v in params.items())}"

        return redirect(full_url)

    except SocialApp.DoesNotExist:
        # Handle case where Google Social App is not configured
        return redirect('login_error')  # Or handle as appropriate


urlpatterns = [
    path('adminn/', admin.site.urls),
    path('', include('adminapp.urls')),
    path('', include('user.urls')),
    path('accounts/', include('allauth.urls')),
    path('accounts/google/direct/', direct_google_login, name='direct_google_login'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
