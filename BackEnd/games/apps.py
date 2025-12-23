from django.apps import AppConfig

class GamesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'games'

    # signals.py 쓰려면 등록 필요!
    def ready(self):
        import games.signals