#ai_analysis/views.py
from django.shortcuts import get_object_or_404
from asgiref.sync import async_to_sync
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from games.models import Game, UserGameLibrary
from .models import AIAnalysisLog
from .serializers import AIAnalysisLogSerializer
from .utils import get_ai_response, parse_ai_json

class GameRecommendationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        force_update = request.data.get('force_update', False)

        # 1. 기존 분석 로그 확인
        if not force_update:
            existing_log = AIAnalysisLog.objects.filter(user=user).first()
            if existing_log:
                serializer = AIAnalysisLogSerializer(existing_log)
                return Response(serializer.data, status=status.HTTP_200_OK)

        # 2. 분석할 게임 데이터 추출
        filtered_games = UserGameLibrary.objects.filter(user=user, playtime_total__gt=0)\
            .select_related('game')
        
        if not filtered_games.exists():
            return Response({"error": "분석할 게임이 없습니다."}, status=status.HTTP_400_BAD_REQUEST)

        game_list_str = ", ".join([f"{e.game.title}({int(e.playtime_total/60)}시간)" for e in filtered_games])

        try:
            # 3. AI 분석 실행 (gpt-5-nano 사용)
            result_json = async_to_sync(self.get_ai_analysis)(game_list_str, 'gpt-5-nano')
            
            if not result_json:
                return Response({"error": "AI 분석 결과 파싱에 실패했습니다."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            all_recs = result_json.get('recommendations', [])
            valid_recs = []
            owned_appids = set(UserGameLibrary.objects.filter(user=user).values_list('game__appid', flat=True))

            # 4. 추천된 게임이 DB에 있는지 확인 및 데이터 보정
            for rec in all_recs:
                db_game = Game.objects.filter(title__iexact=rec['title']).first() or \
                           Game.objects.filter(title__icontains=rec['title']).first()
                if db_game:
                    rec['appid'] = db_game.appid
                    rec['is_owned'] = db_game.appid in owned_appids
                    valid_recs.append(rec)
                if len(valid_recs) >= 3:
                    break

            # 5. 결과 저장
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
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    async def get_ai_analysis(self, game_str, model_name):
        system_prompt = (
            "당신은 'Friday'라는 이름의 AI 게임 분석가입니다. 긍정적이고 활기찬 말투를 쓰세요. "
            "유저의 게임 목록을 보고 성향을 분석한 뒤, 추천 게임 7개를 골라주세요. "
            "반드시 보유한 게임 목록에 없는 새로운 게임을 추천해주세요. "
            "반드시 아래의 JSON 형식으로만 답변해야 합니다.\n"
            "{\n"
            "  \"gamer_type\": \"한 줄 요약\",\n"
            "  \"analysis\": \"상세 분석 내용 (3문장)\",\n"
            "  \"recommendations\": [\n"
            "    {\"title\": \"게임명1\", \"reason\": \"추천 이유1\"},\n"
            "    ...\n"
            "  ]\n"
            "}"
        )
        user_prompt = f"안녕 Friday! 내가 즐겨하는 게임들이야: [{game_str}]. 성향 분석과 추천 부탁해!"
        
        # 통합 유틸리티 함수 사용
        raw_res = await get_ai_response(model_name, system_prompt, user_prompt)
        return parse_ai_json(raw_res)