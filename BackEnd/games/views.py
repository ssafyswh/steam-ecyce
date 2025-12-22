import requests
from thefuzz import process, fuzz # thefuzz 사용
from datetime import datetime
from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from .models import Game, Tag
from .serializers import GameSerializer

# --- Helper 함수는 변경 없음 (생략) ---
def fetch_game_detail_internal(appid):
    url = "https://store.steampowered.com/api/appdetails"
    params = {"appids": appid, "l": "koreana", "cc": "kr"}
    try:
        response = requests.get(url, params=params, timeout=3)
        data = response.json()
        if not data or str(appid) not in data or not data[str(appid)]['success']:
            return None
        game_data = data[str(appid)]['data']
        price = 0
        if 'price_overview' in game_data:
            price = game_data['price_overview']['final'] / 100 
        elif game_data.get('is_free'):
            price = 0
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
        return {
            "publisher": game_data.get('publishers', [''])[0],
            "release_date": release_date,
            "price": price,
            "description": game_data.get('short_description', ''),
            "header_image": game_data.get('header_image', ''),
            "genres_list": [g['description'] for g in game_data.get('genres', [])],
            "categories_list": [c['description'] for c in game_data.get('categories', [])]
        }
    except Exception as e:
        print(f"Steam App Detail Error ({appid}): {e}")
        return None

# --- ViewSet ---
class GameViewSet(viewsets.ModelViewSet):
    queryset = Game.objects.all().order_by('-release_date')
    serializer_class = GameSerializer
    lookup_field = 'appid'
    
    filter_backends = [filters.SearchFilter]
    search_fields = ['title']

    def _update_game_info_if_needed(self, instance):
        if not instance.header_image or not instance.description:
            detail_data = fetch_game_detail_internal(instance.appid)
            if detail_data:
                instance.publisher = detail_data['publisher']
                instance.release_date = detail_data['release_date']
                instance.price = detail_data['price']
                instance.description = detail_data['description']
                instance.header_image = detail_data['header_image']
                instance.genres = detail_data['genres_list'] # 문자열 저장 필요 시 join 사용
                instance.save() 
                if detail_data['categories_list']:
                    for tag_name in detail_data['categories_list']:
                        tag_obj, _ = Tag.objects.get_or_create(name=tag_name)
                        instance.tags.add(tag_obj)
                return True
        return False

    # 👇 [수정됨] 길이 필터링이 추가된 스마트 검색 로직
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        search_query = request.query_params.get('search', None)
        
        suggested_query = None
        search_message = None

        if not queryset.exists() and search_query:
            all_titles = list(Game.objects.values_list('title', flat=True))
            
            # [핵심 수정] "G" 같은 노이즈 제거
            # 검색어 길이의 50% 이상인 제목만 후보로 남김
            # 예: 'legedn'(6글자) -> 최소 3글자 이상의 게임만 비교 ('G' 탈락)
            candidates = [t for t in all_titles if len(t) >= len(search_query) * 0.5]

            # [핵심 수정] WRatio 사용 (Partial + Full Score 종합 고려)
            if candidates:
                best_match = process.extractOne(search_query, candidates, scorer=fuzz.WRatio)
                
                # 점수 기준을 75점으로 살짝 상향
                if best_match and best_match[1] >= 75:
                    suggested_title = best_match[0]
                    suggested_query = suggested_title
                    
                    # 정확한 제목으로 재검색
                    queryset = self.get_queryset().filter(title=suggested_title)
                    if not queryset.exists():
                        queryset = self.get_queryset().filter(title__icontains=suggested_title)

                    search_message = f"'{search_query}'에 대한 결과가 없어 '{suggested_title}'(으)로 검색했습니다."

        page = self.paginate_queryset(queryset)
        if page is not None:
            for game in page:
                self._update_game_info_if_needed(game)
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
            
            if suggested_query:
                response.data['search_info'] = {
                    "original_query": search_query,
                    "suggested_query": suggested_query,
                    "message": search_message
                }
            return response

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    # retrieve 메서드 등 나머지는 동일
    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
        except Exception:
            return Response(status=status.HTTP_404_NOT_FOUND)
        self._update_game_info_if_needed(instance)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)