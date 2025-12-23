# games/views.py
import requests
from datetime import datetime, timedelta
from django.conf import settings
from django.db.models import Case, When, Value, IntegerField
from django.utils import timezone
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework import status
from .models import UserGameLibrary, Game, Tag
from .serializers import UserGameLibrarySerializer
from asgiref.sync import async_to_sync, sync_to_async
from ai_analysis.views import get_search_recommendations


# [중요] 이 함수는 다른 뷰에서도 쓸 수 있게 클래스 밖으로 뺐습니다.
def fetch_game_detail_internal(appid):
    """ 스팀 상점 API에서 게임 상세 정보를 가져오는 함수 """
    url = "https://store.steampowered.com/api/appdetails"
    params = {"appids": appid, "l": "koreana", "cc": "kr"}
    
    try:
        response = requests.get(url, params=params, timeout=1)
        data = response.json()
        
        if not data or str(appid) not in data or not data[str(appid)]['success']:
            return None

        game_data = data[str(appid)]['data']
        
        # 가격 파싱
        price = 0
        if 'price_overview' in game_data:
            price = game_data['price_overview']['final'] // 100
        
        # 날짜 파싱
        release_date = None
        date_str = game_data.get('release_date', {}).get('date', '')
        if date_str:
            for fmt in ["%Y년 %m월 %d일", "%d %b, %Y", "%Y-%m-%d"]:
                try:
                    release_date = datetime.strptime(date_str, fmt).date()
                    break
                except ValueError: continue

        return {
            "publisher": game_data.get('publishers', [''])[0],
            "release_date": release_date,
            "price": price,
            "description": game_data.get('short_description', ''),
            "header_image": game_data.get('header_image', ''),
            "genres": [g['description'] for g in game_data.get('genres', [])],
        }
    except Exception:
        return None

# === 1. 내 라이브러리 조회 및 동기화 ===
class SteamLibrary(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        library = UserGameLibrary.objects.filter(user=request.user).order_by('-playtime_total')
        serializer = UserGameLibrarySerializer(library, many=True)
        return Response(serializer.data)

    def post(self, request):
        user = request.user
        steam_id = user.username
        
        if not steam_id:
            return Response({"error": "스팀 ID가 없습니다."}, status=400)

        url = "http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/"
        params = {
            "key": settings.STEAM_API_KEY,
            "steamid": steam_id,
            "format": "json",
            "include_appinfo": 1,
            "include_played_free_games": 1,
        }
        
        try:
            res = requests.get(url, params=params)
            games_data = res.json().get("response", {}).get("games", [])
            
            updated_count = 0
            for info in games_data:
                game, _ = Game.objects.get_or_create(
                    appid=info['appid'],
                    defaults={'title': info['name']}
                )
                if not game.header_image:
                    detail = fetch_game_detail_internal(info['appid'])
                    if detail:
                        game.publisher = detail['publisher']
                        game.release_date = detail['release_date']
                        game.price = detail['price']
                        game.description = detail['description']
                        game.header_image = detail['header_image']
                        game.genres = ", ".join(detail['genres'])
                        game.save()
                
                
                UserGameLibrary.objects.update_or_create(
                    user=user, game=game,
                    defaults={'playtime_total': info.get('playtime_forever', 0), 'playtime_recent_2weeks': info.get('playtime_2weeks', 0)}
                )
                updated_count += 1
            
            return Response({"message": "동기화 성공", "updated_count": updated_count})
        except Exception as e:
            return Response({"error": str(e)}, status=500)

# === 2. 게임 상세 조회 (자동 업데이트 기능 포함) ===
class GameDetailView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, appid):
        game = get_object_or_404(Game, appid=appid)

        # 정보가 갱신된지 하루 이상이 지났을 경우 재갱신
        now = timezone.now()
        if not game.description or (game.updated_at and now - game.updated_at > timedelta(days=1)):
            print(f"🔄 {game.title} 상세 정보 업데이트 중...")
            detail = fetch_game_detail_internal(appid)
            if detail:
                game.publisher = detail['publisher']
                game.release_date = detail['release_date']
                game.price = detail['price']
                game.description = detail['description']
                game.header_image = detail['header_image']
                game.genres = ", ".join(detail['genres'])
                game.save()
                
                
                # for tag_name in detail['tags']:
                #     tag, _ = Tag.objects.get_or_create(name=tag_name)
                #     game.tags.add(tag)

        # 플레이타임 계산
        playtime = ''
        is_owned = False
        if request.user.is_authenticated:
            ug = UserGameLibrary.objects.filter(user=request.user, game=game).first()
            if ug: 
                playtime = ug.playtime_total
                is_owned = True

        return Response({
            'appid': game.appid,
            'title': game.title,
            'header_image': game.header_image,
            'description': game.description,
            'publisher': game.publisher,
            'price': game.price,
            'playtime_total': playtime,
            'is_owned': is_owned,
            'genres': game.genres,
            'release_date': game.release_date
        })
    
''' 
Django ORM은 기본적으로 동기 방식이므로 비동기 뷰(async def) 안에서 DB를 조회하려면
sync_to_async로 감싸서 실행해야 에러가 발생하지 않는다.
'''
class GameSearchView(APIView):
    def serialize_game(self, game):
        return {
            "appid": game.appid,
            "title": game.title,
            "header_image": game.header_image,
            "price": game.price,
        }
    
    def get(self, request):
        query = request.GET.get('q', '').strip()
        limit = request.GET.get('limit') # limit 파라미터 받기 (예: 20)
        offset = request.GET.get('offset', 0)
        
        if not query:
            return Response({"error": "검색어를 입력해주세요."}, status=status.HTTP_400_BAD_REQUEST)

    
        # 검색 쿼리셋 생성
        qs = Game.objects.filter(title__icontains=query).annotate(
            search_priority=Case(
                When(title__istartswith=query, then=Value(0)),
                default=Value(1),
                output_field=IntegerField(),
            )
        ).order_by('search_priority', 'title')
        
        # 전체 개수 계산
        total_count = qs.count()
        
        # paging 처리
        try:
            off_int = int(offset)
            if limit:
                lim_int = int(limit)
                qs = qs[off_int : off_int + lim_int]
        except ValueError:
            pass
         
        games_list = list(qs)
        results_data = []
        recommendations = []
                
        if total_count > 0:
            # 검색 결과가 있는 경우
            results_data = [self.serialize_game(g) for g in games_list]
        else:
            # 검색 결과가 없으면 AI 추천 로직 실행
            ai_results = async_to_sync(get_search_recommendations)(query)
            print(f"DEBUG: AI가 반환한 원본 결과 -> {ai_results}")
            
            if ai_results:
                # AI가 준 appid들을 추출
                suggested_appids = [item['appid'] for item in ai_results if 'appid' in item]
                print(f"DEBUG: 추출된 appid들 -> {suggested_appids}")
                
                def get_valid_recommendations(appids):
                    # AI가 준 appid 중 우리 DB에 실제 존재하는 게임만 필터링
                    return list(Game.objects.filter(appid__in=appids))

                rec_games = get_valid_recommendations(suggested_appids)
                print(f"DEBUG: 우리 DB에서 찾은 게임 개수 -> {len(rec_games)}")
                recommendations = [self.serialize_game(g) for g in rec_games]

        # 최종 응답 구조 반환
        return Response({
            "count": total_count,
            "results": results_data,
            "recommendations": recommendations # AI 추천 결과 추가
        }, status=status.HTTP_200_OK)