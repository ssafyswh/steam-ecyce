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

from games.models import Game, UserGameLibrary
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

        # 게임 데이터 가져오기(플레이타임이 0이 아닌 게임들의 전체 목록)
        filtered_games = UserGameLibrary.objects.filter(user=user, playtime_total__gt=0)\
            .select_related('game')\
            # .order_by('-playtime_total')[:10]
        
        if not filtered_games.exists():
            return Response({"error": "분석할 게임이 없습니다."}, status=status.HTTP_400_BAD_REQUEST)

        owned_titles = [entry.game.title for entry in filtered_games]
        game_list_str = ", ".join([f"{e.game.title}({int(e.playtime_total/60)}시간)" for e in filtered_games])
        print(f"DEBUG: AI 분석 시작 (새로 생성) - {user}")

        try:
            # AI 호출 (비동기 -> 동기)
            result_json = async_to_sync(self.get_ai_analysis)(game_list_str)
            
            # 추천된 게임이 이미 라이브러리에 있는지 확인
            all_recs = result_json.get('recommendations', [])
            valid_recs = []
            
            # 유저의 전체 라이브러리 (보유 여부 체크용)
            owned_appids = set(UserGameLibrary.objects.filter(user=user).values_list('game__appid', flat=True))
            for rec in all_recs:
                # ai의 추천 결과를 기반으로 db에서 검색
                # 완전 일치(iexact) 혹은 포함(icontains)으로 검색
                db_game = Game.objects.filter(title__iexact=rec['title']).first() or \
                           Game.objects.filter(title__icontains=rec['title']).first()
                if db_game:
                    rec['appid'] = db_game.appid
                    if db_game.appid in owned_appids:
                        rec['is_owned'] = True
                    else:
                        rec['is_owned'] = False
                    # db 검색 성공(유효) 결과만 저장 
                    valid_recs.append(rec)
                if len(valid_recs) >= 3:
                    break

            # 결과 DB에 저장
            log, _ = AIAnalysisLog.objects.update_or_create(
                user=user,
                defaults={
                    'gamer_type': result_json.get('gamer_type'),
                    'analysis_text': result_json.get('analysis'),
                    'recommendations': valid_recs,
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
            "유저의 게임 목록을 보고 성향을 분석한 뒤, 추천 게임 7개를 골라주세요. "
            "반드시 보유한 게임 목록에 없는 새로운 게임을 추천해주세요. "
            "게임의 제목은 반드시 제공된 게임 목록의 제목 형식을 참고해서 똑같이 작성해주세요. "
            "반드시 아래의 JSON 형식으로만 답변해야 합니다.\n"
            "{\n"
            "  \"gamer_type\": \"한 줄 요약\",\n"
            "  \"analysis\": \"상세 분석 내용 (3문장)\",\n"
            "  \"recommendations\": [\n"
            "    {\"title\": \"게임명1\", \"reason\": \"추천 이유1\"},\n"
            "    {\"title\": \"게임명2\", \"reason\": \"추천 이유2\"},\n"
            "    {\"title\": \"게임명3\", \"reason\": \"추천 이유3\"}\n"
            "    {\"title\": \"게임명4\", \"reason\": \"추천 이유4\"}\n"
            "    {\"title\": \"게임명5\", \"reason\": \"추천 이유5\"}\n"
            "    {\"title\": \"게임명6\", \"reason\": \"추천 이유6\"}\n"
            "    {\"title\": \"게임명7\", \"reason\": \"추천 이유7\"}\n"
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
