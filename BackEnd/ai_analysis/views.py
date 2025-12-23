# ai_analysis/views.py
import environ
import json
import re
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

# 검색 결과가 없을 때, 검색어와 유사한 실제 게임 제목을 AI에게 물어보는 기능
async def get_search_recommendations(query):
    client = get_ai_client()
    
    system_prompt = (
        "당신은 스팀 게임 데이터베이스 전문가입니다. 사용자의 검색어를 분석할 때:\n"
        "1. 오타가 있다면 'PUBG: BATTLEGROUNDS', 'Eternal Return'처럼 정확한 공식 명칭으로 교정하세요.\n"
        "2. 반드시 실제 존재하는 Steam AppID만 제공하세요. 확실하지 않다면 해당 항목은 제외하세요.\n"
        "3. appid가 확실한지 검증하기 위해 해당 게임의 스팀 상점 페이지의 url을 참고하세요. 스팀 상점 페이지의 url 형식은 다음과 같습니다: https://store.steampowered.com/app/(appid)\n"
        "4. 최신 게임보다 인지도가 높은 메이저 게임 위주로 매칭하세요.\n"
        "반드시 JSON 리스트 형식으로만 응답하세요."
        "예시: [{\"appid\": 1049590, \"title\": \"Eternal Return\"}]"
    )
    
    user_prompt = f"사용자 검색어 '{query}'와 가장 유사한 게임 3개의 appid와 제목을 JSON으로 알려주세요."

    try:
        response = await client.chat.completions.create(
            # 왠지 모르겠는데 5-nano 모델 쓰니까 작동안됨
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            
            max_completion_tokens=300,
        )
        if not response.choices or not response.choices[0].message.content:
            print("🚨 [AI 에러] 응답 본문이 비어있습니다. 모델명이나 API 키를 확인하세요.")
            return []
        
        # 응답 refine
        raw_content = response.choices[0].message.content.strip()
        print(f"📡 [AI 원본 응답]: {raw_content}")
        start_idx = raw_content.find('[')
        end_idx = raw_content.rfind(']')
        
        if start_idx != -1 and end_idx != -1 and start_idx < end_idx:
            content = raw_content[start_idx : end_idx + 1]
        else:
            # 리스트 형태가 없으면 전체 내용을 사용
            content = raw_content

        if not content:
            print("🚨 [AI 에러] 유효한 JSON 구간을 찾을 수 없습니다.")
            return []

        # 5. JSON 파싱 및 구조 정규화
        data = json.loads(content)
        
        # 만약 리스트가 아니라 딕셔너리로 왔을 경우 대응
        if isinstance(data, dict):
            for key in ['recommendations', 'games', 'results']:
                if key in data and isinstance(data[key], list):
                    return data[key]
            # 딕셔너리 내부의 첫 번째 리스트를 반환하거나 단일 객체를 리스트화
            for val in data.values():
                if isinstance(val, list): return val
            return [data]
            
        return data if isinstance(data, list) else []

    except json.JSONDecodeError as e:
        print(f"❌ [JSON 파싱 에러]: {e}")
        print(f"👉 문제의 텍스트: {content}")
        return []
    except Exception as e:
        print(f"❌ [AI 서비스 에러]: {e}")
        return []