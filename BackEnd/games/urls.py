from django.urls import path
from .views import SteamLibrary, GameDetailView

urlpatterns = [
    path('library/', SteamLibrary.as_view(), name='library'),
    path('<int:appid>/', GameDetailView.as_view(), name='game-detail')
]