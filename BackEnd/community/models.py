# community/models.py
from django.db import models
from django.conf import settings
from games.models import Game

class Articles(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE, null=True, blank=True)

    title = models.CharField(max_length=100)
    article = models.TextField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title}"
    
# 이미지 전용 모델
class ArticleImage(models.Model):
    article = models.ForeignKey(Articles, on_delete=models.CASCADE, related_name='images')
    # 이미지 파일 저장 (media/article_images/ 폴더에 저장됨)
    image = models.ImageField(upload_to='article_images/')
    
    def __str__(self):
        return f"{self.article.title} - image"