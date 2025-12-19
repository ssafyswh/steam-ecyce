import requests
import time
from django.conf import settings
from django.core.management.base import BaseCommand
from games.models import Game

class Command(BaseCommand):
    help = 'Steam IStoreService API를 통해 게임 목록을 페이지네이션하여 수집합니다.'

    def handle(self, *args, **kwargs):
        api_key = getattr(settings, 'STEAM_API_KEY', None)
        if not api_key:
            self.stdout.write(self.style.ERROR('API Key가 설정되지 않았습니다. .env 파일을 확인해주세요.'))
            return

        self.stdout.write("Steam 게임 목록 수집 시작 (IStoreService/GetAppList/v1)...")

        # 초기 설정
        base_url = "https://api.steampowered.com/IStoreService/GetAppList/v1/"
        last_appid = 0  # 처음엔 0부터 시작
        total_collected = 0
        more_games = True

        # 이미 DB에 있는 app_id 캐싱 (중복 방지용)
        existing_app_ids = set(Game.objects.values_list('app_id', flat=True))

        while more_games:
            params = {
                "key": api_key,
                "last_appid": last_appid, # 이 값이 계속 변하면서 다음 페이지를 요청함
                "max_results": 50000,     # 한 번에 가져올 최대 개수 (안전하게 5만 설정)
                "include_games": "true",  # 게임만 포함
                "include_dlc": "false",   # DLC 제외
                "include_software": "false", # 소프트웨어 제외
                # "have_description_only": "false" # 필요하면 추가
            }

            try:
                self.stdout.write(f"요청 중... (last_appid: {last_appid})")
                response = requests.get(base_url, params=params, timeout=10)
                
                if response.status_code != 200:
                    self.stdout.write(self.style.ERROR(f"API 요청 실패: {response.status_code}"))
                    break

                data = response.json()
                
                # 응답 구조: {'response': {'apps': [...]}}
                response_data = data.get('response', {})
                apps = response_data.get('apps', [])

                if not apps:
                    self.stdout.write("더 이상 가져올 게임이 없습니다.")
                    more_games = False
                    break

                # DB 저장 준비
                game_list = []
                current_batch_last_id = 0

                for app in apps:
                    app_id = str(app['appid'])
                    title = app['name']
                    current_batch_last_id = app['appid'] # 마지막 ID 기억해두기

                    # 1. 중복 체크
                    if app_id in existing_app_ids:
                        continue
                    
                    # 2. 타이틀 유효성 체크
                    if not title:
                        continue

                    game_list.append(
                        Game(
                            app_id=app_id,
                            title=title[:255]
                        )
                    )
                    # 처리된 ID는 existing set에도 추가해야 같은 배치 내 중복도 방지됨
                    existing_app_ids.add(app_id)

                # Bulk Create
                if game_list:
                    Game.objects.bulk_create(game_list, batch_size=5000)
                    total_collected += len(game_list)
                    self.stdout.write(f"  -> {len(game_list)}개 저장 완료.")
                
                # 다음 페이지를 위해 last_appid 갱신
                last_appid = current_batch_last_id
                
                # API 호출 빈도 조절 (너무 빠르면 차단될 수 있으므로 1초 대기)
                time.sleep(1)

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"에러 발생: {e}"))
                break

        self.stdout.write(self.style.SUCCESS(f'모든 작업 완료! 총 추가된 게임 수: {total_collected}개'))