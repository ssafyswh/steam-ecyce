# games/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views


# DRF의 라우터를 사용하면 RESTful 표준 URL을 자동으로 생성해줍니다.
router = DefaultRouter()
router.register(r'games', views.GameViewSet)


urlpatterns = [
    path('', include(router.urls)),
]