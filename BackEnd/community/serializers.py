# community/serializers.py
from rest_framework import serializers
from .models import Articles, ArticleImage

class ArticleImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(use_url=True)

    class Meta:
        model = ArticleImage
        fields = ['id', 'image']

class ArticleSerializer(serializers.ModelSerializer):
    # 읽기 전용: 게시글 조회 시 이미지를 중첩해서 보여줌
    images = ArticleImageSerializer(many=True, read_only=True)
    game_id = serializers.IntegerField(required=False, allow_null=True, write_only=True)

    class Meta:
        model = Articles
        fields = [
            'id', 'user', 'title', 'article', 'game_id', 'images', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ('user',)