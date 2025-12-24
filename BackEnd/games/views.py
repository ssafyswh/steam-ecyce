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
from .models import UserGameLibrary, Game, UserFavoriteGame
from .serializers import UserGameLibrarySerializer
from asgiref.sync import async_to_sync, sync_to_async
from ai_analysis.views import get_search_recommendations
from ai_analysis.models import ReviewSummary
from ai_analysis.utils import fetch_steam_reviews, get_ai_review_summary

def get_or_create_review_summary(game):
    # 1. 이미 완료된 요약이 있는지 확인
    summary, created = ReviewSummary.objects.get_or_create(game=game)
    
    if created or summary.status != 'COMPLETED':
        summary.status = 'PROCESSING'
        summary.save()
        
        # 2. 스팀 리뷰 크롤링
        reviews = fetch_steam_reviews(game.appid)
        
        if reviews:
            # 3. AI 분석 실행 (자연스러운 문단 생성)
            ai_text = async_to_sync(get_ai_review_summary)(reviews)
            
            # 4. DB 저장
            summary.summary_text = ai_text
            summary.status = 'COMPLETED'
            summary.save()
        else:
            summary.status = 'FAILED'
            summary.save()
            
    return summary

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
                
        from .serializers import GameSerializer
        serializer = GameSerializer(game)
        data = serializer.data

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
            
        data.update({
            'playtime_total': playtime,
            'is_owned': is_owned,
            'is_favorite': is_favorite,
        })
        return Response(data)
    
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
    
    
class AnalyzeGameReviewsView(APIView):
    def post(self, request, appid):
        try:
            # 1. 대상 게임 찾기
            game = Game.objects.get(appid=appid)
            
            # 2. ReviewSummary 객체 가져오거나 생성
            summary, created = ReviewSummary.objects.get_or_create(game=game)
            
            # 잦은 api 호출 제한!
            if not created and summary.status == 'COMPLETED':
                time_diff = timezone.now() - summary.last_updated_at
                if time_diff < timedelta(minutes=30):
                    # 30분이 지나지 않았다면 기존 데이터를 그대로 반환
                    return Response({
                        "message": "최근 30분 이내에 분석된 데이터가 있습니다.",
                        "data": self.serialize_summary(summary)
                    }, status=status.HTTP_200_OK)
            
            # 3. 상태 업데이트 (이미 완료된 상태여도 재분석 요청이 오면 다시 실행)
            summary.status = 'PROCESSING'
            summary.save()
            
            # 4. 리뷰 수집 (utils.py 함수 사용)
            reviews = fetch_steam_reviews(appid)
            
            if not reviews:
                summary.status = 'FAILED'
                summary.summary_text = "스팀에 등록된 유저 리뷰가 부족하여 분석할 수 없습니다."
                summary.save()
                return Response(self.serialize_summary(summary), status=status.HTTP_200_OK)

            # 5. AI 분석 실행 (비동기 함수를 동기적으로 호출)
            # 텍스트만 리스트 형식 없이 하나의 문단으로 받아옴
            ai_text = async_to_sync(get_ai_review_summary)(reviews)
            
            # 6. 결과 저장 및 상태 완료
            summary.summary_text = ai_text
            summary.status = 'COMPLETED'
            summary.save()
            
            return Response(self.serialize_summary(summary), status=status.HTTP_200_OK)

        except Game.DoesNotExist:
            return Response({"error": "게임 정보를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(f"🚨 분석 에러: {str(e)}")
            if 'summary' in locals():
                summary.status = 'FAILED'
                summary.save()
            return Response({"error": "분석 중 오류가 발생했습니다."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def serialize_summary(self, summary):
        """ReviewSummary 모델 데이터를 사전형으로 변환"""
        return {
            "status": summary.status,
            "summary_text": summary.summary_text,
            "last_updated_at": summary.last_updated_at,
            "tokens_used": summary.tokens_used
        }

    
