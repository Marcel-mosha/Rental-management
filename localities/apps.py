from django.apps import AppConfig


class LocalitiesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'localities'
    
    def ready(self):
        # Import signals if they exist
        try:
            import localities.signals
        except ImportError:
            pass
