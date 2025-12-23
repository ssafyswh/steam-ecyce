# games/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import UserFavoriteGame

# 유저가 생성되면 자동으로 좋아하는 게임 테이블에 생성!
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_favorite_game(sender, instance, created, **kwargs):
    if created:
        UserFavoriteGame.objects.create(user=instance)