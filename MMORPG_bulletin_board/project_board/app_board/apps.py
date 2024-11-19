from django.apps import AppConfig


class AppBoardConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_board'

    def ready(self):
        from . import signals
