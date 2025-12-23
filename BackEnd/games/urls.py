from django.urls import path
from .views import SteamLibrary, GameDetailView, GameSearchView, FavoriteGame

urlpatterns = [
    # 내 라이브러리 (목록 및 동기화)
    path('library/', SteamLibrary.as_view(), name='steam-library'),
    
    # 게임 상세 정보 (DB 없으면 크롤링)
    path('<int:appid>/', GameDetailView.as_view(), name='game-detail'),

    # 스마트 검색용
    path('search/', GameSearchView.as_view(), name='game-search'),
    
    # 좋아하는 게임 정보 등록
    path('favorite/', FavoriteGame.as_view(), name='favorite'),
]