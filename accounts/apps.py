from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'
    
    def ready(self):
        # Import signals if they exist
        try:
            import accounts.signals
        except ImportError:
            pass
