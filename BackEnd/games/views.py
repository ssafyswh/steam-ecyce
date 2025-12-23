# games/views.py
import requests
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework import status
from .models import UserGameLibrary, Game, Tag, UserFavoriteGame
from .serializers import UserGameLibrarySerializer

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
        is_favorite = False

        if request.user.is_authenticated:
            ug = UserGameLibrary.objects.filter(user=request.user, game=game).first()
            if ug: 
                playtime = ug.playtime_total
                is_owned = True

            try:
                fav_record = UserFavoriteGame.objects.get(user=request.user)
                if fav_record.game and fav_record.game.appid == game.appid:
                    is_favorite = True
            except UserFavoriteGame.DoesNotExist:
                pass

        return Response({
            'appid': game.appid,
            'title': game.title,
            'header_image': game.header_image,
            'description': game.description,
            'publisher': game.publisher,
            'price': game.price,
            'playtime_total': playtime,
            'is_owned': is_owned,
            'is_favorite': is_favorite,
            'genres': game.genres,
            'release_date': game.release_date
        })

# 월드컵으로 좋아하는 게임을 저장하고 조회하자!
class FavoriteGame(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            fav = UserFavoriteGame.objects.get(user=request.user)
            if fav.game:
                return Response({'game_id': fav.game.appid})
            else:
                return Response({'game_id': None})
        except UserFavoriteGame.DoesNotExist:
            return Response({'game_id': None})

    def post(self, request):
        game_id = request.data.get('game_id')
        if not game_id:
            return Response({'error': 'game_id is required'}, status=400)

        # 게임이 실제로 존재하는지 확인
        game = get_object_or_404(Game, pk=game_id)

        # 유저의 FavoriteGame 객체 가져오기
        favorite, created = UserFavoriteGame.objects.get_or_create(user=request.user)
        favorite.game = game
        favorite.save()

        return Response({'message': 'Favorite game updated', 'game': game.title})

    