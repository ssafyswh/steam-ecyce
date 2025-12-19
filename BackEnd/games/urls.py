from django.urls import path
from .views import SteamLibrary

urlpatterns = [
    path('library/', SteamLibrary.as_view(), name='library'),
]