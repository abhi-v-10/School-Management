from django.apps import AppConfig


class ExamsappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'examsApp'

    def ready(self):
        import examsApp.signals  # noqa: F401
