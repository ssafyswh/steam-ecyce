# games/views.py
import requests
from datetime import datetime, timedelta
from django.conf import settings
from django.db.models import Case, When, Value, IntegerField, Q
from django.utils import timezone
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework import status

from asgiref.sync import async_to_sync
from .models import UserGameLibrary, Game, UserFavoriteGame
from .serializers import UserGameLibrarySerializer, GameSerializer
from ai_analysis.models import ReviewSummary
from ai_analysis.utils import (
    fetch_steam_reviews, 
    get_ai_review_summary, 
    get_ai_response, 
    parse_ai_json
)

# --- 내부 헬퍼 함수 ---
def fetch_game_detail_internal(appid):
    """ 스팀 상점 API에서 게임 상세 정보를 가져오는 함수 """
    url = "https://store.steampowered.com/api/appdetails"
    params = {"appids": appid, "l": "koreana", "cc": "kr"}
    
    try:
        response = requests.get(url, params=params, timeout=5)
        data = response.json()
        
        if not data or str(appid) not in data or not data[str(appid)]['success']:
            return None

        game_data = data[str(appid)]['data']
        
        price = 0
        if 'price_overview' in game_data:
            price = game_data['price_overview']['final'] // 100
        
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

# --- AI 검색 추천 비동기 함수 ---
async def get_search_recommendations(query):
    system_prompt = (
        "당신은 스팀 게임 데이터베이스 전문가입니다. 사용자의 검색어에 대해 "
        "가장 유사한 실제 스팀 게임 3개를 찾아서 반드시 JSON 리스트 형식으로만 답변하세요."
    )
    user_prompt = f"사용자 검색어 '{query}'와 가장 유사한 게임 3개의 appid와 제목을 JSON으로 알려주세요."
    
    raw_res = await get_ai_response('gemini-2.5-flash-lite', system_prompt, user_prompt)
    return parse_ai_json(raw_res) or []


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
                    defaults={
                        'playtime_total': info.get('playtime_forever', 0), 
                        'playtime_recent_2weeks': info.get('playtime_2weeks', 0)
                    }
                )
                updated_count += 1
            
            return Response({"message": "동기화 성공", "updated_count": updated_count})
        except Exception as e:
            return Response({"error": str(e)}, status=500)


# === 2. 게임 상세 조회 ===
class GameDetailView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, appid):
        game = get_object_or_404(Game, appid=appid)
        now = timezone.now()
        
        if not game.description or (game.updated_at and now - game.updated_at > timedelta(days=1)):
            detail = fetch_game_detail_internal(appid)
            if detail:
                game.publisher = detail['publisher']
                game.release_date = detail['release_date']
                game.price = detail['price']
                game.description = detail['description']
                game.header_image = detail['header_image']
                game.genres = ", ".join(detail['genres'])
                game.save()
                
        serializer = GameSerializer(game)
        data = serializer.data

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
            
        data.update({
            'playtime_total': playtime,
            'is_owned': is_owned,
            'is_favorite': is_favorite,
        })
        return Response(data)


# === 3. 게임 검색 (AI 추천 포함) ===
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
        limit = request.GET.get('limit')
        offset = request.GET.get('offset', 0)
        
        if not query:
            return Response({"error": "검색어를 입력해주세요."}, status=status.HTTP_400_BAD_REQUEST)

        qs = Game.objects.filter(title__icontains=query).annotate(
            search_priority=Case(
                When(title__istartswith=query, then=Value(0)),
                default=Value(1),
                output_field=IntegerField(),
            )
        ).order_by('search_priority', 'title')
        
        total_count = qs.count()
        
        try:
            off_int = int(offset)
            if limit:
                lim_int = int(limit)
                qs = qs[off_int : off_int + lim_int]
        except ValueError:
            pass
         
        games_list = list(qs)
        results_data = [self.serialize_game(g) for g in games_list]
        recommendations = []
                
        if total_count == 0:
            ai_results = async_to_sync(get_search_recommendations)(query)
            if ai_results:
                suggested_appids = [item.get('appid') for item in ai_results if item.get('appid')]
                rec_games = Game.objects.filter(appid__in=suggested_appids)
                recommendations = [self.serialize_game(g) for g in rec_games]

        return Response({
            "count": total_count,
            "results": results_data,
            "recommendations": recommendations
        }, status=status.HTTP_200_OK)


# === 4. 선호 게임 저장 (월드컵 결과) ===
class FavoriteGame(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            fav = UserFavoriteGame.objects.get(user=request.user)
            return Response({'game_id': fav.game.appid if fav.game else None})
        except UserFavoriteGame.DoesNotExist:
            return Response({'game_id': None})

    def post(self, request):
        game_id = request.data.get('game_id')
        if not game_id:
            return Response({'error': 'game_id is required'}, status=400)

        game = get_object_or_404(Game, appid=game_id)
        favorite, created = UserFavoriteGame.objects.get_or_create(user=request.user)
        favorite.game = game
        favorite.save()

        return Response({'message': 'Favorite game updated', 'game': game.title})


# === 5. 리뷰 AI 요약 ===
class AnalyzeGameReviewsView(APIView):
    def post(self, request, appid):
        game = get_object_or_404(Game, appid=appid)
        summary, created = ReviewSummary.objects.get_or_create(game=game)
        
        if not created and summary.status == 'COMPLETED':
            if timezone.now() - summary.last_updated_at < timedelta(minutes=30):
                return Response({
                    "message": "최근 분석된 데이터가 있습니다.",
                    "data": self.serialize_summary(summary)
                })
        
        summary.status = 'PROCESSING'
        summary.save()
        
        try:
            reviews = fetch_steam_reviews(appid)
            if not reviews:
                summary.status = 'FAILED'
                summary.summary_text = "분석할 리뷰가 없습니다."
                summary.save()
            else:
                ai_text = async_to_sync(get_ai_review_summary)(reviews)
                summary.summary_text = ai_text
                summary.status = 'COMPLETED'
                summary.save()
            
            return Response(self.serialize_summary(summary))
        except Exception as e:
            summary.status = 'FAILED'
            summary.save()
            return Response({"error": str(e)}, status=500)

    def serialize_summary(self, summary):
        return {
            "status": summary.status,
            "summary_text": summary.summary_text,
            "last_updated_at": summary.last_updated_at,
            "tokens_used": summary.tokens_used
        }

class GameListView(APIView):
    def get(self, request):
        # 1. 파라미터 수신
        genre_param = request.GET.get('genre', '') # "Action,RPG" 형태로 들어옴
        min_price = request.GET.get('min_price')
        max_price = request.GET.get('max_price')
        sort_option = request.GET.get('sort', 'recent') 
        limit = int(request.GET.get('limit', 24))
        offset = int(request.GET.get('offset', 0))
        
        qs = Game.objects.all()

        # 2. 다중 장르 필터링 (OR 조건: 선택한 장르 중 하나라도 포함되면 검색)
        # 만약 AND 조건(모두 포함)을 원하시면 Q 결합 방식을 & 로 바꾸면 됩니다.
        if genre_param:
            genres = [g.strip() for g in genre_param.split(',') if g.strip()]
            if genres:
                q_objects = Q()
                for g in genres:
                    # genres__icontains는 콤마로 구분된 문자열에서 검색
                    q_objects &= Q(genres__icontains=g) 
                qs = qs.filter(q_objects)
        
        # 3. 가격 범위 필터링
        if min_price is not None and min_price != '':
            qs = qs.filter(price__gte=int(min_price))
            
        if max_price is not None and max_price != '':
            qs = qs.filter(price__lte=int(max_price))

        # 4. 정렬
        if sort_option == 'price_asc':
            qs = qs.order_by('price')
        elif sort_option == 'price_desc':
            qs = qs.order_by('-price')
        elif sort_option == 'name':
            qs = qs.order_by('title')
        else:
            qs = qs.order_by('-release_date', '-appid')

        # 5. 페이징 및 응답
        total_count = qs.count()
        qs = qs[offset : offset + limit]
        
        data = []
        for game in qs:
            data.append({
                "appid": game.appid,
                "title": game.title,
                "header_image": game.header_image,
                "price": game.price,
                "genres": game.genres,
                "release_date": game.release_date
            })

        return Response({
            "count": total_count,
            "results": data
        }, status=status.HTTP_200_OK)
