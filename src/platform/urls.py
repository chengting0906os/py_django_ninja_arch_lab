"""URL configuration for Django + Ninja Extra."""

from django.contrib import admin
from django.urls import path

from src.platform.api import api


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', api.urls),
]
