# games/views.py
import requests
from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import UserGameLibrary, Game
from .serializers import UserGameLibrarySerializer 


class SteamLibrary(APIView):
    permission_classes = [IsAuthenticated]

    # 내 라이브러리 조회
    def get(self, request):
        user = request.user
        # 유저가 가진 게임들을 가져옴 (플레이타임 많은 순 정렬)
        my_library = UserGameLibrary.objects.filter(user=user).select_related('game').order_by('-playtime_total')
        
        serializer = UserGameLibrarySerializer(my_library, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        print('hihihihi')
        user = request.user
        steam_id = user.username
        
        if not steam_id:
            return Response({"error": "스팀 ID가 존재하지 않습니다."}, status=status.HTTP_400_BAD_REQUEST)

        # Steam API 호출 
        url = "http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/"
        params = {
            "key": settings.STEAM_API_KEY,
            "steamid": steam_id,
            "format": "json",
            "include_appinfo": 1, # 게임 이름, 아이콘 등 정보 포함
            "include_played_free_games": 1 # 무료 게임 포함
        }

        try:
            response = requests.get(url, params=params)
            data = response.json()
            
            # 스팀 응답 구조 확인
            if "response" not in data or "games" not in data["response"]:
                # 프로필 비공개이거나 게임이 없는 경우
                return Response({"message": "게임 목록을 가져올 수 없습니다. 프로필 공개 설정을 확인해주세요."}, status=status.HTTP_404_NOT_FOUND)
            
            games_data = data["response"]["games"]
            
            updated_count = 0
            
            # 데이터 DB에 저장
            for game_info in games_data:
                appid = game_info.get("appid")
                title = game_info.get("name")
                playtime_forever = game_info.get("playtime_forever", 0) # 총 플레이타임 (분)
                playtime_2weeks = game_info.get("playtime_2weeks", 0)   # 최근 2주 (분)
                header_url = f"https://steamcdn-a.akamaihd.net/steam/apps/{appid}/header.jpg"

                # Game 모델 생성 또는 가져오기
                game_obj, created = Game.objects.get_or_create(
                    appid=appid,
                    defaults={
                        "title": title,
                        "header_image": header_url,
                    } # 게임이 없을 때만 저장
                )

                # UserGameLibrary 모델 생성 또는 업데이트
                library_entry, created = UserGameLibrary.objects.update_or_create(
                    user=user,
                    game=game_obj,
                    defaults={
                        "playtime_total": playtime_forever,
                        "playtime_recent_2weeks": playtime_2weeks,
                    }
                )
                updated_count += 1

            return Response({
                "message": "라이브러리 동기화 성공",
                "total_games": len(games_data),
                "updated_count": updated_count,
                "user": user.nickname
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class GameDetailView(APIView):
    def get(self, request, appid):
        game = get_object_or_404(Game, appid=appid)
        user_game = UserGameLibrary.objects.filter(user=request.user, game=game).first()

        data = {
            'title': game.title,
            'header_image': game.header_image,
            'description': game.description,
            'playtime_total': user_game.playtime_total if user_game else 0,
            # 나중에 AI 호출하기
        }
        return Response(data)
    

# ============================================================================
# ============================================================================
# ============================================================================
# ============================================================================
# ============================================================================

from datetime import datetime
from rest_framework import viewsets, filters
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
