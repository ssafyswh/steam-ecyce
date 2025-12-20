from rest_framework import serializers
from .models import Game, UserGameLibrary

class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = ['appid', 'title', 'header_image', 'price']

class UserGameLibrarySerializer(serializers.ModelSerializer):
    game = GameSerializer(read_only=True)

    class Meta:
        model = UserGameLibrary
        fields = ['game', 'playtime_total', 'playtime_recent_2weeks', 'last_updated_at']