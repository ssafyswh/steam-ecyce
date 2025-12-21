import requests
from datetime import datetime
from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from .models import Game, Tag
from .serializers import GameSerializer

# --- Helper Function (views.py 내부 함수) ---
def fetch_game_detail_internal(appid):
    """
    Steam Store API를 통해 상세 정보를 가져옵니다.
    장르(Genre)와 태그(Category)를 구분해서 파싱합니다.
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
        
        # 데이터 유효성 검사
        if not data or str(appid) not in data or not data[str(appid)]['success']:
            return None

        game_data = data[str(appid)]['data']
        
        # 가격 처리
        price = 0
        if 'price_overview' in game_data:
            price = game_data['price_overview']['final'] / 100 
        elif game_data.get('is_free'):
            price = 0

        # 날짜 처리
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
        
        # 1. 장르 (Genre) -> "Action", "RPG" (큰 분류)
        genre_list = [g['description'] for g in game_data.get('genres', [])]

        # 2. 태그/카테고리 (Category) -> "Single-player", "Co-op" (기능적 분류)
        # Steam API에서는 이를 'categories'라고 부릅니다.
        category_list = [c['description'] for c in game_data.get('categories', [])]

        return {
            "publisher": game_data.get('publishers', [''])[0],
            "release_date": release_date,
            "price": price,
            "description": game_data.get('short_description', ''),
            "header_image": game_data.get('header_image', ''),
            "genres_list": genre_list,      # 장르 리스트
            "categories_list": category_list # 태그 리스트
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
        if not instance.header_image or not instance.description:
            # 내부 함수 호출
            detail_data = fetch_game_detail_internal(instance.appid)
            
            if detail_data:
                # 1. 기본 정보 업데이트
                instance.publisher = detail_data['publisher']
                instance.release_date = detail_data['release_date']
                instance.price = detail_data['price']
                instance.description = detail_data['description']
                instance.header_image = detail_data['header_image']
                
                # 2. 장르 (Genre) 처리 -> CharField에 문자열로 저장
                # 예: "Action, RPG"
                instance.genres = ", ".join(detail_data['genres_list'])
                
                # M2M 저장을 위해 인스턴스 먼저 저장
                instance.save()

                # 3. 태그 (Tag) 처리 -> Tag 모델(M2M)에 저장
                # Steam의 'categories' 데이터를 Tag 테이블에 넣습니다.
                if detail_data['categories_list']:
                    for tag_name in detail_data['categories_list']:
                        # Tag 생성 또는 조회
                        tag_obj, created = Tag.objects.get_or_create(name=tag_name)
                        # Game과 Tag 연결
                        instance.tags.add(tag_obj)
                
                return True
        return False

    # 1. 목록 조회 (Pagination + Auto Update)
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            for game in page:
                self._update_game_info_if_needed(game)
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

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