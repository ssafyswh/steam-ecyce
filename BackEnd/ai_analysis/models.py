from django.db import models
from games.models import Game
from django.core.validators import MinValueValidator, MaxValueValidator

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

    