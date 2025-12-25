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
    # 1. [조회용] 프론트엔드 표시 및 이동을 위한 필드 (ReadOnly)
    user_nickname = serializers.ReadOnlyField(source='user.nickname')
    user_avatar = serializers.ReadOnlyField(source='user.avatar')
    game_title = serializers.ReadOnlyField(source='game.title')
    game_image = serializers.ReadOnlyField(source='game.header_image') # 사진 출력용
    game_appid = serializers.ReadOnlyField(source='game.appid')       # 상세페이지 이동용(Steam ID)
    
    # 2. [계산용] 플레이 타임 정보
    playtime_info = serializers.SerializerMethodField()
    
    # 3. [생성용] 프론트에서 POST 보낼 때 사용하는 필드 (WriteOnly)
    game_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Review
        fields = [
            'id', 'user', 'user_nickname', 'user_avatar',
            'game_id', 'game_appid', 'game_title', 'game_image',
            'rating_fun', 'rating_story', 'rating_control', 'rating_sound', 'rating_optimization',
            'content', 'playtime_info',
            'created_at', 'updated_at'
        ]
        # user는 request.user에서 가져오므로 읽기 전용으로 설정
        read_only_fields = ('user', 'game_title', 'game_image', 'game_appid')

    def get_playtime_info(self, obj):
        try:
            library = UserGameLibrary.objects.get(user=obj.user, game=obj.game)
            return {
                'total_hours': round(library.playtime_total / 60, 1),
                'recent_hours': round(library.playtime_recent_2weeks / 60, 1)
            }
        except (UserGameLibrary.DoesNotExist, AttributeError):
            return {'total_hours': 0, 'recent_hours': 0}

    def create(self, validated_data):
        game_id = validated_data.pop('game_id')
        
        try:
            # 실제 Game 객체를 찾음
            game = Game.objects.get(appid=game_id)
        except Game.DoesNotExist:
            raise serializers.ValidationError({"game_id": "존재하지 않는 게임입니다."})
        
        # 현재 유저 정보 가져오기 (context 이용)
        user = self.context['request'].user
        
        # 중복 리뷰 체크 (선택 사항이지만 권장)
        if Review.objects.filter(user=user, game=game).exists():
            raise serializers.ValidationError({"detail": "이미 이 게임에 대한 리뷰를 작성했습니다."})
            
        # views.py에서 serializer.save(user=...)를 했으므로 user는 이미 주머니에 있음
        validated_data['game'] = game

        # 6. 부모 클래스의 create를 호출하면 DRF가 알아서 중복 없이 잘 저장해줌
        return super().create(validated_data)