# community/models.py
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from games.models import Game

class Article(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE, null=True, blank=True)

    title = models.CharField(max_length=100)
    content = models.TextField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title}"

class Comment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user.nickname}: {self.content[:20]}'
    
class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='community_reviews')
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='community_reviews')
    
    # 5가지 평가 지표 (1~5점)
    rating_fun = models.IntegerField(default=0, validators=[MinValueValidator(1), MaxValueValidator(5)])
    rating_story = models.IntegerField(default=0, validators=[MinValueValidator(1), MaxValueValidator(5)])
    rating_control = models.IntegerField(default=0, validators=[MinValueValidator(1), MaxValueValidator(5)])
    rating_sound = models.IntegerField(default=0, validators=[MinValueValidator(1), MaxValueValidator(5)])
    rating_optimization = models.IntegerField(default=0, validators=[MinValueValidator(1), MaxValueValidator(5)])
    
    content = models.TextField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # 한 유저가 하나의 게임에 대해 중복 리뷰 작성 불가
        unique_together = ('user', 'game')

    def __str__(self):
        return f"{self.user} - {self.game.title} Review"