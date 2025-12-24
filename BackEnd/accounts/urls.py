#accounts/urls.py
from django.urls import path
from .views import SteamLoginUrlView, SteamLoginVerifyView, UserDetailView, Logout_view, MyPageView

urlpatterns = [
    path('steam/url/', SteamLoginUrlView.as_view()),
    path('steam/verify/', SteamLoginVerifyView.as_view()),
    path('user/me/', UserDetailView.as_view(), name='user_detail'),
    path('logout/', Logout_view, name='logout'),
    path('user/mypage/', MyPageView.as_view(), name='mypage'),
]