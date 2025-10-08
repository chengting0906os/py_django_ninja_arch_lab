"""URL configuration for Django + Ninja Extra."""

from django.urls import path

from src.platform.config.api import api


urlpatterns = [
    path('api/', api.urls),
]
