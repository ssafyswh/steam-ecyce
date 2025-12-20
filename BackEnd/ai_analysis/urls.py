from django.urls import path
from . import views

urlpatterns = [
    path('recommend/', views.GameRecommendationView.as_view(), name='ai-recommend'),
]