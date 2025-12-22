# accounts/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
import requests
from urllib.parse import urlencode
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

User = get_user_model()

class SteamLoginUrlView(APIView):
    # 스팀 로그인 페이지 URL 생성
    def get(self, request):
        steam_openid_url = "https://steamcommunity.com/openid/login"
        params = {
            "openid.ns": "http://specs.openid.net/auth/2.0",
            "openid.identity": "http://specs.openid.net/auth/2.0/identifier_select",
            "openid.claimed_id": "http://specs.openid.net/auth/2.0/identifier_select",
            "openid.mode": "checkid_setup",
            "openid.return_to": f"{settings.FRONTEND_URL}/auth/callback",
            "openid.realm": settings.FRONTEND_URL,
        }
        auth_url = f"{steam_openid_url}?{urlencode(params)}"
        return Response({"url": auth_url})

class SteamLoginVerifyView(APIView):
    # 스팀 로그인 검증 및 토큰 발급 (심플 버전)
    def post(self, request):
        steam_data = request.data.copy()
        steam_data["openid.mode"] = "check_authentication"
        
        # 스팀에 검증 요청
        response = requests.post("https://steamcommunity.com/openid/login", data=steam_data)
        
        if "is_valid:true" in response.text:
            claimed_id = steam_data.get("openid.claimed_id")
            steam_id = claimed_id.split("/")[-1]
            
            # 유저가 DB에 있다면 불러오고, 없다면 생성
            user, created = User.objects.get_or_create(username=steam_id)
            
            # 스팀 유저 정보 업데이트
            try:
                api_key = settings.STEAM_API_KEY 
                player_url = "http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/"
                
                res = requests.get(player_url, params={"key": api_key, "steamids": steam_id})
                data = res.json()
                
                # 데이터 파싱
                if "response" in data and len(data["response"]["players"]) > 0:
                    player_info = data["response"]["players"][0]
                    
                    # 정보 추출
                    new_nickname = player_info.get("personaname")
                    new_avatar = player_info.get("avatarfull")
                    
                    # DB 업데이트 (정보가 바뀌었을 수도 있으니 매번 갱신)
                    user.nickname = new_nickname
                    user.avatar = new_avatar
                    user.save()

            except Exception as e:
                print(f"스팀 유저 정보 가져오기 실패 (로그인은 진행함): {e}")
            # ---------------------------------------------------------

            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            
            res = Response({
                'token': access_token,
                "message": "Login success",
                "steam_id": steam_id
            }, status=status.HTTP_200_OK)

            # Access Token 쿠키 설정
            res.set_cookie(
                key='access_token',
                value=str(refresh.access_token),
                httponly=True,  # 자바스크립트 접근 불가
                samesite='Lax', # CSRF 보호 및 프론트/백 통신 허용
                secure=False,   # localhost에서는 False여야 함 (배포시 True)
                max_age=3600    # 1시간
            )

            # Refresh Token 쿠키 설정
            res.set_cookie(
                key='refresh_token',
                value=str(refresh),
                httponly=True,
                samesite='Lax',
                secure=False,
                max_age=3600 * 24 # 24시간
            )

            return res
        else:
            return Response({"error": "Steam authentication failed"}, status=status.HTTP_400_BAD_REQUEST)
        
class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # request.user : 토큰을 통해 식별된 현재 유저 객체
        return Response({
            "id": request.user.id,
            "username": request.user.username, # 스팀 ID
            "nickname": request.user.nickname, # 스팀 닉네임
            "avatar": request.user.avatar,     # 이미지 URL
            "is_active": request.user.is_active,
        })
    
@api_view(['POST'])
@permission_classes([AllowAny])
def Logout_view(request):
    response = Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)
    
    # 쿠키 삭제
    response.delete_cookie('access_token')
    response.delete_cookie('refresh_token')
    
    return response