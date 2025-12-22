# ai_analysis/views.py
import json
import environ
from pathlib import Path
from asgiref.sync import async_to_sync
from openai import AsyncOpenAI

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from games.models import UserGameLibrary
from .models import AIAnalysisLog
from .serializers import AIAnalysisLogSerializer

BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env(DEBUG=(bool, False))
env_file = BASE_DIR / '.env'
if env_file.exists():
    environ.Env.read_env(env_file)

def get_ai_client():
    api_key = env('OPENAI_API_KEY')
    return AsyncOpenAI(
        api_key=api_key,
        base_url="https://gms.ssafy.io/gmsapi/api.openai.com/v1"
    )

class GameRecommendationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        
        # 강제 업데이트 여부 확인 (force_update가 true면 재분석)
        force_update = request.data.get('force_update', False)

        # DB에 저장된 기록이 있고, 강제 업데이트가 아니면 저장된 거 반환
        if not force_update:
            existing_log = AIAnalysisLog.objects.filter(user=user).first()
            if existing_log:
                print("DEBUG: DB에서 기존 분석 결과 로드")
                serializer = AIAnalysisLogSerializer(existing_log)
                return Response(serializer.data, status=status.HTTP_200_OK)

        # 게임 데이터 가져오기
        top_games = UserGameLibrary.objects.filter(user=user)\
            .select_related('game')\
            .order_by('-playtime_total')[:10]
        
        if not top_games.exists():
            return Response({"error": "분석할 게임이 없습니다."}, status=status.HTTP_400_BAD_REQUEST)

        game_list = [f"{entry.game.title}({int(entry.playtime_total/60)}시간)" for entry in top_games]
        game_list_str = ", ".join(game_list)
        print(f"DEBUG: AI 분석 시작 (새로 생성) - {user}")

        try:
            # AI 호출 (비동기 -> 동기)
            result_json = async_to_sync(self.get_ai_analysis)(game_list_str)
            
            # 결과 DB에 저장
            log, created = AIAnalysisLog.objects.update_or_create(
                user=user,
                defaults={
                    'gamer_type': result_json.get('gamer_type'),
                    'analysis_text': result_json.get('analysis'),
                    'recommendations': result_json.get('recommendations'),
                }
            )
            
            return Response(AIAnalysisLogSerializer(log).data, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"ERROR: {e}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    async def get_ai_analysis(self, game_str):
        client = get_ai_client()
        system_prompt = (
            "당신은 'Friday'라는 이름의 AI 게임 분석가입니다. 긍정적이고 활기찬 말투를 쓰세요. "
            "유저의 게임 목록을 보고 성향을 분석한 뒤, 추천 게임 3개를 골라주세요. "
            "반드시 아래의 JSON 형식으로만 답변해야 합니다.\n"
            "{\n"
            "  \"gamer_type\": \"한 줄 요약\",\n"
            "  \"analysis\": \"상세 분석 내용 (3문장)\",\n"
            "  \"recommendations\": [\n"
            "    {\"title\": \"게임명1\", \"reason\": \"추천 이유1\"},\n"
            "    {\"title\": \"게임명2\", \"reason\": \"추천 이유2\"},\n"
            "    {\"title\": \"게임명3\", \"reason\": \"추천 이유3\"}\n"
            "  ]\n"
            "}"
        )
        user_prompt = f"안녕 Friday! 내가 즐겨하는 게임들이야: [{game_str}]. 성향 분석과 추천 부탁해!"
        
        response = await client.chat.completions.create(
             model='gpt-5-nano',
             messages=[
                 {"role": "system", "content": system_prompt},
                 {"role": "user", "content": user_prompt}
             ],
            #  max_tokens=1024
        )
        content = response.choices[0].message.content
        if content.startswith("```json"):
            content = content.replace("```json", "").replace("```", "")
        elif content.startswith("```"):
            content = content.replace("```", "")
        return json.loads(content.strip())



