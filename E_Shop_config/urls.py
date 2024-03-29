"""E_Shop_config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include(), function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.conf import settings

from django.contrib import admin
from django.urls import path, include

from E_Shop_config.yasg import urlpatterns as doc_urls
from E_Shop_Frontend.Products.views import ProductHomeListView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    # FRONTEND APPLICATION
    path('', include('E_Shop_Frontend.Users.urls')),
    path('', include('E_Shop_Frontend.Products.urls')),
    path('', include('E_Shop_Frontend.Cart.urls')),

    # ADMIN PANEL
    path('admin/', admin.site.urls),

    #  GOOGLE OAUTH
    path('', include('allauth.urls')),

    # HOME PAGE
    path('', ProductHomeListView.as_view(), name='home'),

    # API APPLICATION
    path('api/', include('E_Shop_API.E_Shop_Users.urls')),
    path('api/', include('E_Shop_API.E_Shop_Products.urls')),
    path('api/', include('E_Shop_API.E_Shop_Cart.urls')),

    # DJOSER
    path('api/auth/', include('djoser.urls')),

    # JWT TOKEN
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

]
urlpatterns += doc_urls
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
