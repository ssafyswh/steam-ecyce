# community/serializers.py
from rest_framework import serializers
from .models import Article, Comment
from games.models import Game

class CommentSerializer(serializers.ModelSerializer):
    user_nickname = serializers.ReadOnlyField(source='user.nickname')
    user_avatar = serializers.ReadOnlyField(source='user.avatar')

    class Meta:
        model = Comment
        fields = ['id', 'article', 'user', 'user_nickname', 'user_avatar', 'content', 'created_at', 'updated_at']
        read_only_fields = ('user', 'article',)

class ArticleSerializer(serializers.ModelSerializer):
    user_nickname = serializers.ReadOnlyField(source='user.nickname')
    user_avatar = serializers.ReadOnlyField(source='user.avatar')
    game_title = serializers.ReadOnlyField(source='game.title')
    game_image = serializers.ReadOnlyField(source='game.header_image')
    game_id = serializers.IntegerField(write_only=True)
    
    # 해당 게시글에 달린 댓글 목록을 포함 (선택 사항)
    comments = CommentSerializer(many=True, read_only=True)
    # 댓글 개수 카운트
    comment_count = serializers.IntegerField(source='comments.count', read_only=True)

    class Meta:
        model = Article
        fields = [
            'id', 'user', 'user_nickname', 'user_avatar', 
            'title', 'content', 
            'game_id', 'game_title', 'game_image', 
            'comments', 'comment_count', 'created_at', 'updated_at'
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
    
