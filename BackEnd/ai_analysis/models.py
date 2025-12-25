# ai_analysis/models.py
from django.db import models
from games.models import Game
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings

class ReviewSummary(models.Model):
    # 리뷰 요약을 담을 테이블(게임과 1대1)
    game = models.OneToOneField(Game, on_delete=models.CASCADE, related_name='review_summary')
    summary_text = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=[
            ('PENDING', '대기'), 
            ('PROCESSING', '분석중'), 
            ('COMPLETED', '완료'), 
            ('FAILED', '실패')
        ],
        default='PENDING'
    )
    tokens_used = models.IntegerField(default=0)
    last_updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.game.name} 리뷰 AI 요약'

class GameReview(models.Model):
    # 모든 개별 리뷰를 담는 테이블
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='reviews')
    steam_review_id = models.CharField(max_length=50, unique=True)
    content = models.TextField()

    # AI 필터링 결과
    sentiment_score = models.FloatField(
        null=True, 
        blank=True,
        validators=[
            MinValueValidator(-1.0),
            MaxValueValidator(1.0)
        ],
        help_text="감정 점수(-1: 매우 부정, 1: 매우 긍정)")
    is_useful = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.game.name} - 리뷰 번호 {self.steam_review_id}'

class AIAnalysisLog(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ai_analysis')
    
    # 분석 결과 데이터 (칭호, 상세 분석 내용)
    gamer_type = models.CharField(max_length=100)
    analysis_text = models.TextField()
    
    # 추천 게임 목록 JSON 형태로
    # 예: [{"title": "...", "reason": "..."}, ...]
    recommendations = models.JSONField() 
    
    created_at = models.DateTimeField(auto_now_add=True) # 처음 분석한 시간
    updated_at = models.DateTimeField(auto_now=True)     # 다시 분석한 시간

    def __str__(self):
        return f"{self.user} - {self.gamer_type}"