# accounts/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from ai_analysis.models import AIAnalysisLog
from games.models import UserFavoriteGame

User = get_user_model()

class MyPageSerializer(serializers.ModelSerializer):
    # AI 분석 및 최애 게임 정보를 위한 커스텀 필드
    ai_info = serializers.SerializerMethodField()
    favorite_game = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'nickname', 'avatar', 'ai_info', 'favorite_game']

    def get_ai_info(self, obj):
        # AIAnalysisLog 모델에서 유저와 매칭되는 정보 조회
        try:
            # related_name='ai_analysis'를 통해 접근
            analysis = obj.ai_analysis
            return {
                'gamer_type': analysis.gamer_type,
                'analysis_text': analysis.analysis_text,
                'recommendations': analysis.recommendations
            }
        except AttributeError:
            # 아직 분석 기록이 없는 경우
            return None

    def get_favorite_game(self, obj):
        # UserFavoriteGame 모델에서 최애 게임 정보 조회
        try:
            # related_name='favorite_game'을 통해 접근
            fav = obj.favorite_game
            return {
                'appid': fav.game.appid,
                'title': fav.game.title,
                'header_image': fav.game.header_image
            }
        except AttributeError:
            # 아직 최애 게임이 설정되지 않은 경우
            return None