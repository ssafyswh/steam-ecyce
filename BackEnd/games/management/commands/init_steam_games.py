import requests
import time
from django.conf import settings
from django.core.management.base import BaseCommand
from games.models import Game

class Command(BaseCommand):
    help = 'Steam IStoreService API를 통해 게임 목록을 페이지네이션하여 수집합니다.'

    def handle(self, *args, **kwargs):
        # settings.py에서 API Key 가져오기
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

        # 이미 DB에 있는 appid 캐싱 (중복 저장 방지용)
        # models.py의 필드명인 'appid'를 사용합니다.
        existing_appids = set(Game.objects.values_list('appid', flat=True))

        while more_games:
            params = {
                "key": api_key,
                "last_appid": last_appid, # 이 값이 계속 변하면서 다음 페이지를 요청함
                "max_results": 50000,     # 한 번에 가져올 최대 개수
                "include_games": "true",  # 게임만 포함
                "include_dlc": "false",   # DLC 제외
                "include_software": "false", # 소프트웨어 제외
            }

            try:
                self.stdout.write(f"요청 중... (last_appid: {last_appid})")
                response = requests.get(base_url, params=params, timeout=30)
                
                if response.status_code != 200:
                    self.stdout.write(self.style.ERROR(f"API 요청 실패: {response.status_code}"))
                    break

                data = response.json()
                
                # 응답 구조 파싱
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
                    # API가 주는 키는 'appid', models.py의 필드명도 'appid'
                    current_appid = int(app['appid'])
                    title = app['name']
                    current_batch_last_id = app['appid'] # 다음 페이지 요청을 위해 숫자형 ID 기억

                    # 1. 중복 체크 (이미 DB에 있으면 패스)
                    if current_appid in existing_appids:
                        continue
                    
                    # 2. 타이틀 유효성 체크 (빈 제목 제외)
                    if not title:
                        continue

                    # 3. 객체 생성
                    # models.py의 필드명에 맞춰서 생성합니다.
                    # publisher, description 등의 필드는 null=True이므로 여기서 안 채워도 에러 안 남
                    game_list.append(
                        Game(
                            appid=current_appid,  # models.py의 appid 필드
                            title=title[:255]     # max_length=255 제한 준수
                        )
                    )
                    # 중복 방지 세트에도 추가 (현재 배치 내 중복 방지)
                    existing_appids.add(current_appid)

                # Bulk Create (한 번에 저장)
                if game_list:
                    Game.objects.bulk_create(game_list, batch_size=5000)
                    total_collected += len(game_list)
                    self.stdout.write(f"  -> {len(game_list)}개 저장 완료.")
                
                # 다음 페이지를 위해 last_appid 갱신
                last_appid = current_batch_last_id
                
                # API 호출 빈도 조절 (1초 대기)
                time.sleep(1)

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"에러 발생: {e}"))
                break

        self.stdout.write(self.style.SUCCESS(f'모든 작업 완료! 총 추가된 게임 수: {total_collected}개'))