#accounts/urls.py
from django.urls import path
from .views import SteamLoginUrlView, SteamLoginVerifyView, UserDetailView, Logout_view, MyPageView, UserWithdrawView

urlpatterns = [
    path('steam/url/', SteamLoginUrlView.as_view()),
    path('steam/verify/', SteamLoginVerifyView.as_view()),
    path('user/me/', UserDetailView.as_view(), name='user_detail'),
    path('logout/', Logout_view, name='logout'),
    path('user/mypage/', MyPageView.as_view(), name='mypage'),
    path('user/withdraw/', UserWithdrawView.as_view(), name='user-withdraw'),
]