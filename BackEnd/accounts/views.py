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

from .serializers import MyPageSerializer

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
    def post(self, request):
        # 1. 임시 로그인 모드 체크
        if getattr(settings, 'MOCK_STEAM_LOGIN', False):
            steam_id = settings.MOCK_STEAM_ID
            user, created = User.objects.get_or_create(username=steam_id)
            
            if created or not user.nickname:
                user.nickname = "임시유저"
                user.avatar = "https://avatars.akamai.steamstatic.com/fef49e7fa7e1997310d705b2a6158ff8dc1cdfeb_full.jpg"
                user.save()

            # 중요: 여기서 바로 return을 해줘야 아래쪽의 steam_id 에러 코드로 내려가지 않습니다.
            return self._generate_success_response(user, steam_id)

        # 2. 실제 스팀 로그인 로직 (정상 상황)
        steam_data = request.data.copy()
        steam_data["openid.mode"] = "check_authentication"
        
        # 에러가 났던 부분 수정: data에는 steam_id가 아니라 steam_data를 넣어야 합니다.
        try:
            response = requests.post("https://steamcommunity.com/openid/login", data=steam_data, timeout=5)
            
            if "is_valid:true" in response.text:
                claimed_id = steam_data.get("openid.claimed_id")
                # 여기서 비로소 steam_id가 정의됩니다.
                steam_id = claimed_id.split("/")[-1]
                user, created = User.objects.get_or_create(username=steam_id)
                
                # ... (중략: 유저 정보 업데이트 로직) ...
                
                return self._generate_success_response(user, steam_id)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        return Response({"error": "Steam authentication failed"}, status=status.HTTP_400_BAD_REQUEST)

    # 응답 생성 헬퍼 함수
    def _generate_success_response(self, user, steam_id):
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        res = Response({'token': access_token, "steam_id": steam_id}, status=status.HTTP_200_OK)
        res.set_cookie(key='access_token', value=access_token, httponly=True, samesite='Lax', secure=False, max_age=3600)
        res.set_cookie(key='refresh_token', value=str(refresh), httponly=True, samesite='Lax', secure=False, max_age=3600 * 24)
        return res
        
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

class UserWithdrawView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        user = request.user
        user.delete()  # DB에서 유저 삭제
        
        response = Response({"message": "회원 탈퇴가 완료되었습니다."}, status=status.HTTP_204_NO_CONTENT)
        
        # 쿠키 삭제 (로그아웃 처리)
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')
        
        return response

class MyPageView(APIView):
    # 인증된 사용자만 접근 가능
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # 현재 토큰의 주인공인 유저(request.user)의 통합 정보를 반환
        serializer = MyPageSerializer(request.user)
        return Response(serializer.data)