from rest_framework import serializers
from .models import Game


class GameSerializer(serializers.ModelSerializer):
    # 명세서 F04의 '상점 페이지' 요구사항을 충족하기 위해 URL 필드 추가
    steam_url = serializers.SerializerMethodField()

    class Meta:
        model = Game
        fields = '__all__'  # 기존 필드들에 steam_url이 자동으로 추가됩니다.

    # app_id를 기반으로 실제 스팀 상점 페이지 링크를 생성하는 함수
    def get_steam_url(self, obj):
        return f"https://store.steampowered.com/app/{obj.app_id}/"