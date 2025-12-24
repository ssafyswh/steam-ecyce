# community/serializers.py
from rest_framework import serializers
from .models import Article
from games.models import Game

class ArticleSerializer(serializers.ModelSerializer):
    # [조회용] 게시글을 볼 때 게임 정보를 같이 보여주기 위함
    game_title = serializers.ReadOnlyField(source='game.title')
    game_image = serializers.ReadOnlyField(source='game.header_image')
    # 작성자 이름도 보이면 좋으므로 추가
    user_name = serializers.ReadOnlyField(source='user.username')

    # [저장용] 프론트에서 전송하는 appid를 받기 위함
    # 모델의 필드명이 game이므로 source='game'을 지정하거나 views에서 처리
    game_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = Article
        fields = [
                    'id', 'user_name', 'title', 'content', 
                    'game_id', 'game_title', 'game_image', 'created_at'
                ]
        read_only_fields = ('user',)

    def create(self, validated_data):
        # 프론트에서 보낸 game_id를 꺼내서 실제 Game 모델과 연결
        game_id = validated_data.pop('game_id', None)
        if game_id:
            try:
                game = Game.objects.get(appid=game_id)
                validated_data['game'] = game
            except Game.DoesNotExist:
                pass # 또는 에러 발생
        return super().create(validated_data)