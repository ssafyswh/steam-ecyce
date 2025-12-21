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