from django.db import models

# Create your models here.
class Game(models.Model):
  # app_id: bigint, UK (Steam AppID)
    # Unique Key(UK) 속성을 추가하여 중복을 방지합니다.
    app_id = models.BigIntegerField(unique=True, help_text="Steam AppID")

    # title: string
    title = models.CharField(max_length=255)

    # publisher: string
    # 퍼블리셔 정보가 없을 수도 있으니, 필요하다면 null=True, blank=True를 추가할 수 있습니다.
    publisher = models.CharField(max_length=255)

    # release_date: date
    release_date = models.DateField()

    # price: decimal
    # 가격은 소수점을 포함할 수 있으므로 DecimalField를 사용합니다.
    # max_digits=10 (전체 자릿수), decimal_places=2 (소수점 자릿수)로 설정했습니다.
    price = models.DecimalField(max_digits=10, decimal_places=2)

    # metacritic_score: float
    # 점수는 소수점일 수 있으므로 FloatField를 사용합니다.
    metacritic_score = models.FloatField(null=True, blank=True)

    class Meta:
        db_table = 'games'  # 테이블 이름을 명시적으로 'games'로 지정

    def __str__(self):
        return self.title