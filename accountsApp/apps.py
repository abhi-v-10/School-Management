from django.apps import AppConfig


class AccountsappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accountsApp'
    def ready(self):
        import accountsApp.signals
