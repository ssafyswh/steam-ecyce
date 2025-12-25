# community/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ArticleViewSet, CommentViewSet, ReviewViewSet

router = DefaultRouter()
router.register(r'articles', ArticleViewSet)
router.register(r'comments', CommentViewSet) 
router.register(r'reviews', ReviewViewSet)

urlpatterns = [
    path('', include(router.urls)),
]