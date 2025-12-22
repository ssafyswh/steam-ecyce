from django.urls import path, include
from .views import SteamLibrary, GameDetailView, GameViewSet

# 라우터 사용하기 위한 패키지
from rest_framework.routers import DefaultRouter
router = DefaultRouter()
router.register(r'games', GameViewSet)

urlpatterns = [
    path('library/', SteamLibrary.as_view(), name='library'),
    path('<int:appid>/', GameDetailView.as_view(), name='game-detail'),
    path('', include(router.urls)),
]