from django.urls import path
from .views import SteamLibrary, GameDetailView

# 혹시나 router 관련 코드가 있다면 지워도 됩니다.
# 우리가 필요한 건 딱 이 두 가지 경로입니다.

urlpatterns = [
    # 1. 내 라이브러리 (목록 및 동기화)
    path('library/', SteamLibrary.as_view(), name='steam-library'),
    
    # 2. 게임 상세 정보 (DB 없으면 크롤링)
    path('<int:appid>/', GameDetailView.as_view(), name='game-detail'),
]