# community/serializers.py
from rest_framework import serializers
from .models import Article, Comment, Review
from games.models import Game, UserGameLibrary

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
    
class ReviewSerializer(serializers.ModelSerializer):
    user_nickname = serializers.ReadOnlyField(source='user.nickname')
    user_avatar = serializers.ReadOnlyField(source='user.avatar')
    game_title = serializers.ReadOnlyField(source='game.title')

    playtime_info = serializers.SerializerMethodField()

    # 쓰기 전용: 프론트에서 넘어오는 game_id
    game_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Review
        fields = [
            'id', 'user', 'user_nickname', 'user_avatar',
            'game_id', 'game_title',
            'rating_fun', 'rating_story', 'rating_control', 'rating_sound', 'rating_optimization',
            'content', 'created_at', 'updated_at'
        ]
        read_only_fields = ('user', 'game_title')

    def create(self, validated_data):
        game_id = validated_data.pop('game_id')
        game = Game.objects.get(appid=game_id)
        
        # 이미 리뷰를 작성했는지 검증 (선택 사항)
        user = self.context['request'].user
        if Review.objects.filter(user=user, game=game).exists():
            raise serializers.ValidationError("이미 이 게임에 대한 리뷰를 작성했습니다.")
            
        review = Review.objects.create(game=game, **validated_data)
        return review
    
    def get_playtime_info(self, obj):
        try:
            # 해당 유저와 해당 게임의 라이브러리 정보를 찾음
            library = UserGameLibrary.objects.get(user=obj.user, game=obj.game)
            return {
                # 분 단위 데이터를 시간 단위로 변환 (소수점 1자리)
                'total_hours': round(library.playtime_total / 60, 1),
                'recent_hours': round(library.playtime_recent_2weeks / 60, 1)
            }
        except UserGameLibrary.DoesNotExist:
            # 라이브러리에 없는 게임을 리뷰할 경우(거의 없겠지만)
            return {'total_hours': 0, 'recent_hours': 0}
