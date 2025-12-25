# accounts/authentication.py
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed

# 쿠키 검증
class CookieJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        raw_token = request.COOKIES.get('access_token')
        
        if raw_token is None:
            return None
        try:
            validated_token = self.get_validated_token(raw_token)
            
            # 2. 검증 성공 여부 확인
            print(f"DEBUG: 토큰 검증 성공! 유저: {self.get_user(validated_token)}")
            
            return self.get_user(validated_token), validated_token
        except Exception as e:
            # 3. 에러 내용 확인
            print(f"DEBUG: 토큰 검증 실패 에러 -> {e}")
            return None