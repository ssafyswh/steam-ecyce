from django.shortcuts import render
from rest_framework import viewsets
from .models import Game
from .serializers import GameSerializer

# Create your views here.
class GameViewSet(viewsets.ModelViewSet):
    """
    게임 목록 조회, 생성, 상세 조회, 수정, 삭제 기능을 제공하는 ViewSet
    """
    # 1. 어떤 데이터를 가져올 것인가? (모든 게임 데이터)
    queryset = Game.objects.all().order_by('-release_date') # 최신 출시일 순으로 정렬
    
    # 2. 어떤 시리얼라이저를 쓸 것인가? (아까 만든 GameSerializer)
    serializer_class = GameSerializer