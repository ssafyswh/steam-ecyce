from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    # 스팀 닉네임 (스팀 id는 username에 저장되어있음)
    nickname = models.CharField(max_length=100, blank=True, null=True)
    
    # 스팀 프로필 사진 URL (avatarfull)
    avatar = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.nickname if self.nickname else self.username