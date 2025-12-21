from django.db import models
from django.conf import settings

class Tag(models.Model):
    # 생성된 태그들을 모두 모아놓는 테이블
    name = models.CharField(max_length=20, unique=True)
    def __str__(self):
        return self.name

class Game(models.Model):
    appid = models.CharField(max_length=50, unique=True, help_text="Steam AppID")

    title = models.CharField(max_length=255)

    publisher = models.CharField(max_length=255, blank=True, default="")

    release_date = models.DateField(null=True, blank=True)

    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    description = models.TextField(null=True, blank=True)

    header_image = models.URLField(max_length=500, null=True, blank=True)
    genres = models.CharField(max_length=255, null=True, blank=True)

    # 다대다 관계 설정
    tags = models.ManyToManyField(Tag, related_name='games')
    # owners = models.ManyToManyField(
    #     settings.AUTH_USER_MODEL,
    #     through='UserGameLibrary',
    #     related_name='owned_games'
    # )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    

# class UserGameLibrary(models.Model):
#     # 유저 개인의 라이브러리 정보
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
#     # 게임 데이터
#     game = models.ForeignKey(Game, on_delete=models.CASCADE)

#     # 플레이타임 관련 필드(단위: 분)
#     playtime_total = models.IntegerField(default=0)
#     playtime_recent_2weeks = models.IntegerField(default=0)