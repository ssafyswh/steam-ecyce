# games/models.py
from django.db import models
from django.conf import settings

class Tag(models.Model):
    # 생성된 태그들을 모두 모아놓는 테이블
    name = models.CharField(max_length=20, unique=True)
    def __str__(self):
        return self.name

class Game(models.Model):
    appid = models.BigIntegerField(primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.IntegerField(default=0)
    publisher = models.CharField(max_length=255, blank=True, null=True)
    header_image = models.URLField(max_length=500, blank=True, null=True)
    release_date = models.DateField(null=True, blank=True)
    genres = models.CharField(max_length=255, null=True, blank=True)

    # 다대다 관계 설정
    tags = models.ManyToManyField(Tag, related_name='games')
    owners = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='UserGameLibrary',
        related_name='owned_games'
    )
    
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    
class UserGameLibrary(models.Model):
    # 유저 개인의 라이브러리 정보
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    # 게임 데이터
    game = models.ForeignKey(Game, on_delete=models.CASCADE)

    # 플레이타임 관련 필드(단위: 분)
    playtime_total = models.IntegerField(default=0)
    playtime_recent_2weeks = models.IntegerField(default=0)

    # 라이브러리 갱신 시점 정보
    last_updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'game') # 중복 소유 방지
    def __str__(self):
        return f"{self.user.username}'s {self.game.title}"

class UserFavoriteGame(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='favorite_game'
    )

    game = models.ForeignKey(
        Game,
        on_delete=models.SET_NULL, # 지우면 NULL로 설정
        null=True,                 
        blank=True,
        related_name='favorited_by_users' # game.favorited_by_users 로 이 게임을 픽한 유저들 조회 가능
    )

    def __str__(self):
        game_title = self.game.title if self.game else "Not selected"
        return f"{self.user.username}'s Best Game: {game_title}"