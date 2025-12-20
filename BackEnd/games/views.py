import requests
from datetime import datetime
from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from .models import Game
from .serializers import GameSerializer

# --- Helper Function (Steam API 통신) ---
def fetch_game_detail(appid):
    """
    Steam Store API를 통해 상세 정보를 가져옵니다.
    """
    url = "https://store.steampowered.com/api/appdetails"
    params = {
        "appids": appid,
        "l": "koreana",
        "cc": "kr"
    }

    try:
        response = requests.get(url, params=params, timeout=3)
        data = response.json()
        
        if not data or str(appid) not in data or not data[str(appid)]['success']:
            return None

        game_data = data[str(appid)]['data']
        
        # 가격
        price = 0
        if 'price_overview' in game_data:
            price = game_data['price_overview']['final'] / 100 
        elif game_data.get('is_free'):
            price = 0

        # 날짜
        release_date = None
        date_str = game_data.get('release_date', {}).get('date', '')
        if date_str:
            formats = ["%Y년 %m월 %d일", "%d %b, %Y", "%b %d, %Y", "%Y-%m-%d"]
            for fmt in formats:
                try:
                    release_date = datetime.strptime(date_str, fmt).date()
                    break
                except ValueError:
                    continue
        
        # 장르
        genre_list = [g['description'] for g in game_data.get('genres', [])]
        genres_str = ", ".join(genre_list) if genre_list else ""

        return {
            "publisher": game_data.get('publishers', [''])[0],
            "release_date": release_date,
            "price": price,
            "description": game_data.get('short_description', ''),
            "header_image": game_data.get('header_image', ''),
            "genres": genres_str,
            "metacritic_score": game_data.get('metacritic', {}).get('score'),
        }

    except Exception as e:
        print(f"Steam API Error ({appid}): {e}")
        return None


# --- ViewSet ---
class GameViewSet(viewsets.ModelViewSet):
    queryset = Game.objects.all().order_by('-release_date')
    serializer_class = GameSerializer
    lookup_field = 'appid'
    
    # 검색 기능
    filter_backends = [filters.SearchFilter]
    search_fields = ['title']

    def _update_game_info_if_needed(self, instance):
        """
        상세 정보가 비어있으면 업데이트를 수행하는 내부 메서드
        """
        # 업데이트 조건: 이미지가 없거나 설명이 없는 경우
        if not instance.header_image or not instance.description:
            detail_data = fetch_game_detail(instance.appid)
            
            if detail_data:
                instance.publisher = detail_data['publisher']
                instance.release_date = detail_data['release_date']
                instance.price = detail_data['price']
                instance.description = detail_data['description']
                instance.header_image = detail_data['header_image']
                instance.genres = detail_data['genres']
                instance.metacritic_score = detail_data['metacritic_score']
                instance.save()
                return True
        return False

    # 1. 목록 조회 (Pagination + Auto Update)
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        # 페이지네이션: 여기서 DB의 전체 결과 중 10개만 딱 잘라서 'page'에 담아줍니다.
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            # page 안에 있는 10개 게임만 검사합니다.
            for game in page:
                self._update_game_info_if_needed(game)
            
            # 업데이트된 10개를 반환합니다.
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        # (혹시나 settings.py에서 페이지네이션을 껐을 경우를 대비한 코드)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    # 2. 상세 조회
    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
        except Exception:
            return Response(status=status.HTTP_404_NOT_FOUND)

        self._update_game_info_if_needed(instance)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)