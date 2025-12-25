# games/serializers.py

from rest_framework import serializers
from .models import Game, UserGameLibrary
from ai_analysis.serializers import ReviewSummarySerializer

class GameSerializer(serializers.ModelSerializer):
    # 명세서 F04의 '상점 페이지' 요구사항을 충족하기 위해 URL 필드 추가
    steam_url = serializers.SerializerMethodField()
    
    review_summary = ReviewSummarySerializer(read_only=True)

    class Meta:
        model = Game
        fields = [
            'appid', 'title', 'publisher', 'developer', 'release_date', 
            'price', 'description', 'header_image', 'genres',
            'steam_url', 'review_summary',
        ]

    # appid를 기반으로 실제 스팀 상점 페이지 링크를 생성하는 함수
    def get_steam_url(self, obj):
        return f"https://store.steampowered.com/app/{obj.appid}/"
    
class UserGameLibrarySerializer(serializers.ModelSerializer):
    game = GameSerializer(read_only=True)

    class Meta:
        model = UserGameLibrary
        fields = ['game', 'playtime_total', 'playtime_recent_2weeks', 'last_updated_at']
